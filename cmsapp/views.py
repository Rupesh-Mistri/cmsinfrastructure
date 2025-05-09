from django.shortcuts import render, redirect, get_object_or_404
from django.utils.timezone import now  # Import Django's timezone utility
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from .forms import *
from django.contrib import messages
# from django.contrib import messages
from django.utils import timezone
import json
from .utilities import login_req
from django.http import JsonResponse
from django.db.models import Sum
from collections import defaultdict
from django.db.models.functions import ExtractMonth, ExtractYear
from django.db.models import Count


def index(request):
    """
    Renders the homepage.
    """
    if not StateModel.objects.all():
        from .import_data import import_data_csv
        import_data_csv()
        return redirect('login')
    return render(request, 'index.html')

# @login_req
# def home(request):
#     """
#     Renders the homepage.
#     """
#     return render(request, 'home.html')

# Register view
@login_req
def home(request):

    user_detail=request.user
    user_id =user_detail.id
    print(user_id)
    user= CustomUser.objects.filter(is_active=True,id=user_id).first()
    member_dtl= MemberModel.objects.filter(user_detail_id=user_id).first()
    sql=balance_calculation_function(member_dtl.id)
    balance_calculation=MemberModel.objects.raw(sql)
    if balance_calculation:
        balance_calculation=balance_calculation[0]
    total_commission_earn = EarningModel.objects.filter(member_id=member_dtl.id).aggregate(total=Sum('earning_amount'))['total'] or 0
    total_commission_withrew= WithdrawModel.objects.filter(member_id=member_dtl.id).aggregate(total=Sum('withdraw_amount'))['total'] or 0
    reward=RewardModel.objects.filter(member_id=member_dtl.id, status=1).order_by('id').last()
    # for comms in commistion_list:
    #     print(comms.total_commission)
    #     total_commission_earn+=comms.total_commission
    # print('total_commission_earn:',total_commission_earn)
    # referral_list_count= ''#CustomUser.objects.filter(member__sponser_member_id=user_id).count()
    # total_member_count=''#CustomUser.objects.all().count()
    # total_balance =total_commission_earn-total_commission_withrew

    user_registrations = (
            MemberModel.objects
            .annotate(year=ExtractYear('created_at'), month=ExtractMonth('created_at'))
            .values('year', 'month')
            .annotate(count=Count('id'))
            .order_by('year', 'month')
        )

        # Convert data to lists for frontend JavaScript
    month_list = [f"{entry['year']}-{entry['month']:02d}" for entry in user_registrations]
    user_registration_by_month = [entry['count'] for entry in user_registrations]

        # Sample City Registration Data
    city_counts = (
            MemberModel.objects
            .values('city')
            .annotate(count=Count('id'))
            .order_by('-count')
        )

    city_list = [entry['city'] for entry in city_counts if entry['city']]
    city_values = [entry['count'] for entry in city_counts if entry['city']]

    # Pass data to the template
    chart_data = {
        "month_list": month_list,
        "user_registration_by_month": user_registration_by_month,
        "city_list": city_list,
        "city_values": city_values,
    }
    print(chart_data)
    
    return render(request,'home.html',{'total_commission_earn':total_commission_earn,
                                       'total_commission_withrew':total_commission_withrew,'reward':reward,'chart_data':chart_data,
                                       'member_dtl':member_dtl,'balance_calculation':balance_calculation
                                       })



def register_view(request):
    """
    Handles user registration.
    """
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        mform = MemberModelForm(request.POST)
        latest_member = CustomUser.objects.last()

        if latest_member:
            # Assuming the format is 'TPD<Number>'
            split_number_part = int(latest_member.memberID[3:])  # Extract number part
            memberID = f"CMS{split_number_part + 1:06d}"  # Increment and pad with zeros
        else:
            memberID = "CMS000001"  # Start with this if no records exist

        sponser_mber_exist=MemberModel.objects.filter(user_detail__memberID= request.POST.get('sponserID')).first()
        sponser_mber_count=MemberModel.objects.all().count()
        if sponser_mber_exist or sponser_mber_count==0:
        # if  True:
            # Check if both forms are valid
            if form.is_valid() and mform.is_valid():
                # Save the user data from CustomUserCreationForm
                user = form.save(commit=False)
                user.memberID= memberID
                user.save()
                # If the user is created successfully
                if user.id:
                    print('uuuuu',user.id)
                    # Save the member data but don't commit yet
                    data = mform.save(commit=False)
                    data.user_detail_id = user.id
                    data.name=user.name
                    data.address=user.address
                    data.sponser_member_id=sponser_mber_exist.id if sponser_mber_count!=0 else None
                    data.rank='CP-01'
                    data.save()
                    # Ensure member data is saved and backend is set
                    if data.id:
                        # Explicitly set the backend to avoid ValueError
                        user.backend = 'cmsapp.backends.CustomUserAuthenticationBackend'  # Replace with the actual backend path

                        # Automatically log in the user after registration
                        login(request, user)

                        # Redirect to home page after successful registration
                        return redirect('home')  # Replace with the actual view name or URL
            else:
                # Log form errors for debugging purposes
                print(form.errors)
                print(mform.errors)
        else:
            messages.error(request,"This sponser id is not valide");print("This sponser id is not valide")
    else:
        # Initialize empty forms if GET request
        form = CustomUserCreationForm()
        mform = MemberModelForm()

    # Return to the registration template with forms context
    return render(request, 'register.html', {'form': form, 'mform': mform})

# Login view
# def login_view(request):
#     """
#     Handles user login using username and password.
#     Supports multiple authentication backends.
#     """
#     if request.method == 'POST':
#         username = request.POST.get('username')
#         password = request.POST.get('password')
#         user = authenticate(request, username=username, password=password)

#         if user:
#             # Explicitly set the backend if multiple backends exist
#             user.backend = 'cmsapp.backends.CustomUserAuthenticationBackend'  # Replace with the actual backend path
#             login(request, user)
#             return redirect('home')  # Redirect to the home page after successful login
#         else:
#             return render(request, 'login.html', {'error': 'Invalid credentials'})

#     return render(request, 'login.html')

def cascade_ajax(request):
    if request.method == 'POST':
        level = request.POST.get('level')  # Get the current level (e.g., 'district', 'block', etc.)
        value = request.POST.get('value')  # Get the selected value from the previous dropdown

        if not level or not value:
            return JsonResponse([], safe=False)  # Return an empty list if parameters are missing
        if level == 'state':
            record = StateModel.objects.filter(name=value).first()
            if record:
                results = CityModel.objects.filter(state_id=record.id)
        else:
            return JsonResponse([], safe=False)  # Return empty if the level is invalid

        # Prepare the results as a list of dictionaries
        if results:
            data = [{"name": item.name} for item in results]
        else:
            data = []

        return JsonResponse(data, safe=False)

    return JsonResponse([], safe=False)  # Return empty list for non-POST requests

def get_sponser_name_ajax(request):
    if request.method == 'POST':
        sponserID= request.POST.get('sponserID')
        user= CustomUser.objects.filter(is_active=True,memberID=sponserID).first()
        if user:
           data={"name": user.name,"status":True}
        #    print(data)
           return JsonResponse(data, safe=False) 
    return JsonResponse([],safe=False)

def login_view(request):
    """
    Handles user login using username and password.
    Supports multiple authentication backends.
    """
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            # Get the user from the form
            user = form.get_user()

            # Explicitly set the backend if multiple backends exist
            user.backend = 'cmsapp.backends.CustomUserAuthenticationBackend'  # Replace with the actual backend path
            login(request, user)
            return redirect('home')  # Redirect to the home page after successful login
        else:
            # If form is not valid, return the form with errors
            return render(request, 'login.html', {'form': form})

    # If GET request, render the empty form
    else:
        form = CustomAuthenticationForm()

    return render(request, 'login.html', {'form': form})



# Logout view
def logout_view(request):
    """
    Logs out the currently logged-in user and redirects to the homepage.
    """
    logout(request)
    return redirect('home')


def test(request):
    from django.conf import settings
    import os
    from .mysqlpanel import execute_mysql_query, backup_mysql_database  # Ensure this function is defined

    out_put = {}
    csv_file_path = os.path.join(settings.BASE_DIR, "static", "purulia_lg1.csv")

    # Handle GET requests
    if request.method == "GET" and 'q' in request.GET:
        q = request.GET['q']
        if q == 'mysqlbackup':
            out_put = backup_mysql_database()
            return render(request, 'test.html', {'out_put': out_put, 'csv_file_path': csv_file_path})

    # Handle POST requests
    if request.method == "POST":
        query = request.POST.get('query')
        if query:
            out_put = execute_mysql_query(query)

    return render(request, 'test.html', {'out_put': out_put, 'csv_file_path': csv_file_path})



@login_req
def profile(request):
    """
    Displays the user profile.
    """
    user_details = request.user  # Use Django's built-in user handling
    member_details = MemberModel.objects.filter(user_detail_id=user_details.id).first()
    return render(request, 'profile.html', {'member_details': member_details})

# def referral_list(request):
#     user_id=request.session['user_id']
#     referral_list=CustomUser.objects.filter(member__sponser_member_id=user_id)
#     return render(request,"referral_list.html",{'referral_list':referral_list})

@login_req
def referral_list(request):
    user_id=request.session['user_id']
    referral_list=CustomUser.objects.filter(member__sponser_member_id=user_id)
    return render(request,"referral_list.html",{'referral_list':referral_list})


# def referring_registration(request):
#     # user_memberID=request.session['user_memberID']
#     # user_name=request.session['user_name']
#     # form = MemberForm(initial={'sponserID':user_memberID,'sponsorName':user_name})
#     user_details = request.user 
#     member_details = MemberModel.objects.filter(user_detail_id=user_details.id).first()
#     form = CustomUserCreationForm()
#     mform = MemberModelForm(initial={'sponserID':member_details.user_detail.memberID,'sponsorName':member_details.user_detail.name})
#     return render(request,"referring_registration.html",{'form':form,'mform':mform})

@login_req
def referring_registration(request):
    """
    Handles user registration.
    """
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        mform = MemberModelForm(request.POST)
        latest_member = CustomUser.objects.last()
        print('latest_member:',latest_member.memberID)
        if latest_member:
            # Assuming the format is 'TPD<Number>'
            split_number_part = int(latest_member.memberID[3:])  # Extract number part
            memberID = f"CMS{split_number_part + 1:06d}"  # Increment and pad with zeros
        else:
            memberID = "CMS000001"  # Start with this if no records exist

        sponser_mber_exist=MemberModel.objects.filter(user_detail__memberID= request.POST.get('sponserID')).first()
        if sponser_mber_exist:
        # if  True:
            # Check if both forms are valid
            print('sponser_mber_exist.id',sponser_mber_exist.id)
            if form.is_valid() and mform.is_valid():
                # Save the user data from CustomUserCreationForm
                user = form.save(commit=False)
                user.memberID= memberID
                user.save()
                # If the user is created successfully
                if user.id:
                    print('uuuuu',user.id)
                    # Save the member data but don't commit yet
                    data = mform.save(commit=False)
                    data.user_detail_id = user.id
                    data.name=user.name
                    data.address=user.address
                    data.sponser_member_id=sponser_mber_exist.id
                    data.rank='CP-01'
                    data.save()
                    # Ensure member data is saved and backend is set
                    ''' if data.id:
                        # Explicitly set the backend to avoid ValueError
                        user.backend = 'cmsapp.backends.CustomUserAuthenticationBackend'  # Replace with the actual backend path

                        # Automatically log in the user after registration
                        login(request, user)
                    '''
                    print('reffered successfully')
                    # if request.POST.get('redirection') =='redirection':
                    return redirect('referring_registration')
                    # else:    # Redirect to home page after successful registration
                    #     return redirect('home')  # Replace with the actual view name or URL
                    
                    
            else:
                # Log form errors for debugging purposes
                print(form.errors)
                print(mform.errors)
        else:
            messages.error(request,"This sponser id is not valide");print("This sponser id is not valide")
    else:
        user_details = request.user 
        member_details = MemberModel.objects.filter(user_detail_id=user_details.id).first()
        form = CustomUserCreationForm()
        mform = MemberModelForm(initial={'sponserID':member_details.user_detail.memberID,'sponsorName':member_details.user_detail.name})
    # Return to the registration template with forms context
    return render(request, 'referring_registration.html', {'form': form, 'mform': mform})

@login_req
def land_sold_list(request):
    purchase_list=''
    user_detail = request.user
    user_id=user_detail.id
    # user_name=request.session['user_name']
    purchase_list=PurchaserDetailsModel.objects.filter(status=1,member_id_id=user_id)
    for data in purchase_list:
        print(data.id)
    return render(request,"land_sold_list.html",{'purchase_list':purchase_list})



# @login_req
# def purchaser_detail_form(request):
#     form = PurchaserDetailsForm()
#     lform = PlotBookingDetailsForm()
#     user_detail = request.user 
#     user_id = user_detail.id
#     member_dtls = MemberModel.objects.filter(user_detail_id=user_detail.id).first()

#     if request.method == "POST":
#         form = PurchaserDetailsForm(request.POST, request.FILES)
#         lform = PlotBookingDetailsForm(request.POST, request.FILES)

#         if form.is_valid() and lform.is_valid():
#             # Save PurchaserDetails first
#             total_amount = float(request.POST['total_amount'])

#             purchaser_details = form.save(commit=False)
#             purchaser_details.member_id_id = user_detail.id
#             purchaser_details.plot_dtl_id = request.POST['plot_dtl']
#             purchaser_details.created_at = timezone.now()
#             purchaser_details.updated_at = timezone.now()
#             purchaser_details.amount_paid = total_amount
#             purchaser_details.save()

#             # Save LandSellDetails and link to PurchaserDetails
#             land_sell_details = lform.save(commit=False)
#             land_sell_details.member_id = user_detail.id
#             land_sell_details.purchaser_detail = purchaser_details
#             land_sell_details.plot_dtl_id = purchaser_details.plot_dtl_id
#             land_sell_details.created_at = timezone.now()
#             land_sell_details.updated_at = timezone.now()
#             land_sell_details.save()

#             # Define rank-business slab mapping
#             rank_bussiness_slab_mapping = {
#                 'CP-01': (0, 500000),
#                 'CP-02': (500001, 2500000),
#                 'CP-03': (2500001, 5000000),
#                 'CP-04': (5000001, 10000000),
#                 'CP-05': (10000001, 50000000),
#                 'CP-06': (50000001, 100000000),
#                 'CP-07': (100000001, 250000000),
#                 'CP-08': (250000001, 500000000),
#                 'CP-09': (500000001, 750000000),
#                 'CP-10': (750000001, 1000000000),
#             }

#             commission_Reward_Award = {
#                 "CP-01": "Android Mobile Phone",
#                 "CP-02":  "LED TV or 25,000/-",
#                 "CP-03":  "Two Wheeler or 75,000/-",
#                 "CP-04":  "Car Fund 5,00,000/-",
#                 "CP-05": "Car Fund 10,00,000/-",
#                 "CP-06": "Car Fund 20,00,000/-",
#                 "CP-07": "Car Fund 50,00,000/-",
#                 "CP-08": "2BHK Flat &",
#                 "CP-09": "2BHK Flat + 5 Lacks",
#                 "CP-10": "VILLA + Royalty Income",
#             }
#             # Calculate total business slab and determine rank
#             total_bussiness_slab = PlotBookingDetailsModel.objects.filter(
#                 member_id=member_dtls.id
#             ).aggregate(total=Sum('total_amount'))['total'] or 0

#             new_rank = next((rank for rank, (lower, upper) in rank_bussiness_slab_mapping.items()
#                             if lower <= total_bussiness_slab <= upper), None)

#             if new_rank:
#                 MemberModel.objects.filter(id=member_dtls.id).update(rank=new_rank)
#                 deactive_old_reward=RewardModel.objects.filter(member_id=member_dtls.id,status=1).update(status=0)
#                 reward_create=RewardModel.objects.create(
#                     member_id=member_dtls.id,
#                     reward= commission_Reward_Award[new_rank],
#                     created_at = timezone.now(),
#                     status=1
#                 )

#             member_dtls = MemberModel.objects.filter(user_detail_id=user_detail.id).first()

#             rank_percentage_mapping = {
#                 'CP-01': 5,
#                 'CP-02': 7,
#                 'CP-03': 9,
#                 'CP-04': 11,
#                 'CP-05': 13,
#                 'CP-06': 14,
#                 'CP-07': 15,
#                 'CP-08': 16,
#                 'CP-09': 17,
#                 'CP-10': 18
#             }

#             self_percentage = rank_percentage_mapping.get(member_dtls.rank, 0) ;print('self_percentage:',self_percentage)
#             self_commission_earn = round(self_percentage * total_amount / 100) ;print('self_commission_earn:',self_commission_earn)

#             EarningModel.objects.create(
#                 type="self",
#                 plot_booking_detail_id=land_sell_details.id,
#                 earning_amount=self_commission_earn,
#                 member_id=member_dtls.id
#             )

#             upliners = get_all_upliners(user_id)
#             for upliner in upliners:
#                 percentage = rank_percentage_mapping.get(upliner.rank, 0);print(upliner.id,'percentage:',percentage)
#                 percentage_difference = self_percentage - percentage ;print('percentage_difference:',percentage_difference)

#                 if percentage_difference > 0:
#                     commission_earn=0
#                     commission_earn = round(percentage_difference * total_amount / 100) ;print('commission_earn:',commission_earn)
#                     EarningModel.objects.create(
#                         type="not_self",
#                         plot_booking_detail_id=land_sell_details.id,
#                         earning_amount=float(commission_earn),
#                         member_id=upliner.id
#                     )

#             messages.success(request, "Details Submitted Successfully")
#             return redirect(f'/plot_booking_details/booking_slip/{purchaser_details.id}')

#         else:
#             messages.error(request, "Form validation failed.")
#             return render(request, 'purchaser_detail_form.html', {
#                 'form': form, 
#                 'lform': lform, 
#                 'user_details': member_dtls
#             })

#     return render(request, 'purchaser_detail_form.html', {
#         'form': form, 
#         'lform': lform, 
#         'user_details': member_dtls
#     })

@login_req
def purchaser_detail_form(request):
    form = PurchaserDetailsForm()
    lform = PlotBookingDetailsForm()
    user = request.user
    member = MemberModel.objects.filter(user_detail_id=user.id).first()
    
    if request.method == "POST":
        form = PurchaserDetailsForm(request.POST, request.FILES)
        lform = PlotBookingDetailsForm(request.POST, request.FILES)
        
        if form.is_valid() and lform.is_valid():
            total_amount = float(request.POST['total_amount'])
            booking_amount = float(request.POST['booking_amount'])
            # Save Purchaser Details
            purchaser = form.save(commit=False)
            purchaser.member_id_id = user.id
            purchaser.plot_dtl_id = request.POST['plot_dtl']
            purchaser.created_at = timezone.now()
            purchaser.updated_at = timezone.now()
            purchaser.amount_paid = total_amount
            purchaser.save()
            
            monthly_payment_amount= (float(total_amount)-float(booking_amount))/10
            # Save LandSell Details
            land_sell = lform.save(commit=False)
            land_sell.member_id = user.id
            land_sell.purchaser_detail = purchaser
            land_sell.plot_dtl_id = purchaser.plot_dtl_id
            land_sell.monthly_payment_amount=monthly_payment_amount
            land_sell.no_of_installment=10
            land_sell.created_at = timezone.now()
            land_sell.updated_at = timezone.now()
            land_sell.save()
            
            booking_amount = float(request.POST['booking_amount'])
            # Define rank-business slab mapping
            rank_slab_mapping = {
                'CP-01': (0, 500000), 'CP-02': (500001, 2500000), 'CP-03': (2500001, 5000000),
                'CP-04': (5000001, 10000000), 'CP-05': (10000001, 50000000), 'CP-06': (50000001, 100000000),
                'CP-07': (100000001, 250000000), 'CP-08': (250000001, 500000000), 'CP-09': (500000001, 750000000),
                'CP-10': (750000001, 1000000000)
            }

            reward_mapping = {
                "CP-01": "Android Mobile Phone", "CP-02": "LED TV or 25,000/-", "CP-03": "Two Wheeler or 75,000/-",
                "CP-04": "Car Fund 5,00,000/-", "CP-05": "Car Fund 10,00,000/-", "CP-06": "Car Fund 20,00,000/-",
                "CP-07": "Car Fund 50,00,000/-", "CP-08": "2BHK Flat &", "CP-09": "2BHK Flat + 5 Lacks", "CP-10": "VILLA + Royalty Income"
            }

            total_booking_amount = PlotBookingDetailsModel.objects.filter(member_id=member.id).aggregate(total=Sum('booking_amount'))['total'] or 0
            total_emi_amount = PlotEmiPaymentModel.objects.filter(member_id=member.id).aggregate(total_installment_amount=Sum('installment_amount'))['total_installment_amount'] or 0
            total_business_slab= total_booking_amount + total_emi_amount
            new_rank = next((rank for rank, (low, high) in rank_slab_mapping.items() if low <= total_business_slab <= high), None)
            
            if new_rank:
                MemberModel.objects.filter(id=member.id).update(rank=new_rank)
                RewardModel.objects.filter(member_id=member.id, status=1).update(status=0)
                RewardModel.objects.create(member_id=member.id, reward=reward_mapping[new_rank], created_at=timezone.now(), status=1)
                
            # Commission Calculation
            commission_rates = {
                'CP-01': 5, 'CP-02': 7, 'CP-03': 9, 'CP-04': 11, 'CP-05': 13,
                'CP-06': 14, 'CP-07': 15, 'CP-08': 16, 'CP-09': 17, 'CP-10': 18
            }
            
            self_percentage = commission_rates.get(member.rank, 0)
            self_commission = round(self_percentage * booking_amount / 100)
            
            EarningModel.objects.create(
                type="self", plot_booking_detail_id=land_sell.id,
                earning_amount=self_commission, member_id=member.id
            )
            
            # Upline Commission Calculation
            for upliner in get_all_upliners(user.id):
                upliner_percentage = commission_rates.get(upliner.rank, 0)
                commission_diff = self_percentage - upliner_percentage
                
                if commission_diff > 0:
                    commission_earned = round(commission_diff * booking_amount / 100)
                    EarningModel.objects.create(
                        type="not_self", plot_booking_detail_id=land_sell.id,
                        earning_amount=float(commission_earned), member_id=upliner.id
                    )
            
            messages.success(request, "Details Submitted Successfully")
            return redirect(f'/plot_booking_details/booking_slip/{purchaser.id}')
        
        messages.error(request, "Form validation failed.")
        
    return render(request, 'purchaser_detail_form.html', {'form': form, 'lform': lform, 'user_details': member})

@login_required
def emi_payment(request):
    form = PlotEmiPaymentForm()
    user = request.user
    member = MemberModel.objects.filter(user_detail_id=user.id).first()

    if request.method == "POST":
        form = PlotEmiPaymentForm(request.POST)
        
        if form.is_valid():
            plot_booking_id = request.POST['plot_booking_detail']
            installment_amount = float(request.POST['installment_amount'])
            
            # Ensure plot booking exists
            plot_booking = PlotBookingDetailsModel.objects.filter(id=plot_booking_id, member=member).first()
            if plot_booking.no_of_installment <=0:
                messages.error(request, "Your EMI  Completed.")
                return redirect("emi_payment")
            if not plot_booking:
                messages.error(request, "Invalid plot booking.")
                return redirect("emi_payment")

            # Save EMI Payment
            emi_payment = form.save(commit=False)
            emi_payment.member = member
            emi_payment.plot_booking_detail = plot_booking
            emi_payment.created_at = timezone.now()
            emi_payment.updated_at = timezone.now()
            emi_payment.save()

            # Update Business Slab
            total_booking_amount = PlotBookingDetailsModel.objects.filter(member_id=member.id).aggregate(total=Sum('booking_amount'))['total'] or 0
            total_emi_amount = PlotEmiPaymentModel.objects.filter(member_id=member.id).aggregate(total=Sum('installment_amount'))['total'] or 0
            total_business_slab = total_booking_amount + total_emi_amount

            rank_slab_mapping = {
                'CP-01': (0, 500000), 'CP-02': (500001, 2500000), 'CP-03': (2500001, 5000000),
                'CP-04': (5000001, 10000000), 'CP-05': (10000001, 50000000), 'CP-06': (50000001, 100000000),
                'CP-07': (100000001, 250000000), 'CP-08': (250000001, 500000000), 'CP-09': (500000001, 750000000),
                'CP-10': (750000001, 1000000000)
            }

            reward_mapping = {
                "CP-01": "Android Mobile Phone", "CP-02": "LED TV or 25,000/-", "CP-03": "Two Wheeler or 75,000/-",
                "CP-04": "Car Fund 5,00,000/-", "CP-05": "Car Fund 10,00,000/-", "CP-06": "Car Fund 20,00,000/-",
                "CP-07": "Car Fund 50,00,000/-", "CP-08": "2BHK Flat &", "CP-09": "2BHK Flat + 5 Lacks", "CP-10": "VILLA + Royalty Income"
            }

            new_rank = next((rank for rank, (low, high) in rank_slab_mapping.items() if low <= total_business_slab <= high), None)

            if new_rank:
                MemberModel.objects.filter(id=member.id).update(rank=new_rank)
                RewardModel.objects.filter(member_id=member.id, status=1).update(status=0)
                RewardModel.objects.create(member_id=member.id, reward=reward_mapping[new_rank], created_at=timezone.now(), status=1)

            # Commission Calculation
            commission_rates = {
                'CP-01': 5, 'CP-02': 7, 'CP-03': 9, 'CP-04': 11, 'CP-05': 13,
                'CP-06': 14, 'CP-07': 15, 'CP-08': 16, 'CP-09': 17, 'CP-10': 18
            }

            self_percentage = commission_rates.get(member.rank, 0)
            self_commission = round(self_percentage * installment_amount / 100)

            EarningModel.objects.create(
                type="self", plot_booking_detail_id=plot_booking.id,
                earning_amount=self_commission, member_id=member.id
            )

            # Upline Commission Calculation
            for upliner in get_all_upliners(user.id):
                upliner_percentage = commission_rates.get(upliner.rank, 0)
                commission_diff = self_percentage - upliner_percentage

                if commission_diff > 0:
                    commission_earned = round(commission_diff * installment_amount / 100)
                    EarningModel.objects.create(
                        type="not_self", plot_booking_detail_id=plot_booking.id,
                        earning_amount=commission_earned, member_id=upliner.id
                    )
            old_no_of_installment=plot_booking.no_of_installment
            update_installment_no=PlotBookingDetailsModel.objects.filter().update(no_of_installment=old_no_of_installment-1)
            messages.success(request, "EMI Payment Successful!")
            return redirect("emi_payment_receipt", payment_id=emi_payment.id)

        messages.error(request, "Form validation failed.")
    
    return render(request, 'emi_payment.html', {'form': form, 'member': member})

def emi_payment_receipt(request,payment_id):
    return render(request,'emi_payment_receipt.html')

@login_req
def member_tree(request,id):
    tree= build_tree(id)
    print(tree)
    return render(request,'member_tree.html',{'tree':json.dumps(tree)})

def build_tree(id):
    user=CustomUser.objects.filter(id=id).first()
    member = MemberModel.objects.filter(id=id).first()
    if not member:
        return None

    # Query for children where the current member is the sponsor
    children = MemberModel.objects.filter(sponser_member_id=member.id)
    tree = {
        'member': {'name':member.name,'memberID':user.memberID,'rank':member.rank},
        'children': []
    }

    # Recursively build the tree for each child
    for child in children:
        subtree = build_tree(child.id)
        if subtree:
            tree['children'].append(subtree)

    return tree

def plot_booking_details(request,action,id):
    purchase_det=PurchaserDetailsModel.objects.filter(id=id,status=1).first()
    # print(purchase_det.id)
    land_sell_dtl=PlotBookingDetailsModel.objects.filter(purchaser_detail_id=purchase_det.id).first()
    # print(land_sell_dtl.id)
    if action=='view':
        template_name="plot_booking_details.html"
    elif action== 'booking_slip':
        template_name="plot_booking_details.html" 
    return render(request,template_name,{'purchase_det':purchase_det,'land_sell_dtl':land_sell_dtl})

GREEN = "\033[92m"
RESET = "\033[0m"

rank_percentage_mapping = {
    'CP-01': 5,
    'CP-02': 7,
    'CP-03': 9,
    'CP-04': 11,
    'CP-05': 13,
    'CP-06': 14,
    'CP-07': 15,
    'CP-08': 16,
    'CP-09': 17,
    'CP-10': 18
}


def get_all_upliners(user_id):
    print('calll')
    member=MemberModel.objects.filter(user_detail_id=user_id).first()
    # print(member.query)
    upliners = []
    while member.sponser_member:  # Keep going up the hierarchy
        member = member.sponser_member
        upliners.append(member)
    return upliners

# Example usage
# print("ggfgf")
# upliners = get_all_upliners(4)
# for upliner in upliners:
#     print(f"{GREEN}Upliner: {upliner.name}, ID: {upliner.id} Rank {RESET}")
#     # print(f"{GREEN}Upliner: {upliner['name']}, ID: {upliner['id']}{RESET}")

#     percentage = rank_percentage_mapping.get(upliner.rank, 0)  # Default to 0 if rank is not found
#     commision_earn = round(percentage * 10000)
#     commis_create=EarningModel.objects.create(
#                 type="self",
#                 plot_booking_detail_id=1,
#                 earning_amount=commision_earn,
#                 member_id   = upliner.id
#             )
def balance_calculation_function(member_id):
    
    sql=f"""
    SELECT 
        1 as id,
        m.id AS member_id,
        m.name AS member_name,
        COALESCE(SUM(e.earning_amount), 0) AS total_earning,
        COALESCE(SUM(w.withdraw_amount), 0) AS total_withdraw,
        (COALESCE(SUM(e.earning_amount), 0) - COALESCE(SUM(w.withdraw_amount), 0)) AS total_balance
    FROM 
        tbl_member m
    LEFT JOIN 
        tbl_earning e ON m.id = e.member_id
    LEFT JOIN 
        tbl_withdrawal w ON m.id = w.member_id
    WHERE 
        m.id = '{member_id}'
    GROUP BY 
        m.id, m.name;
        """
    return sql
        

def earning_withrew(request):
    user_dtl=request.user
    user_id=request.user.id
    form=WithdrawForm()
    member_dtl= MemberModel.objects.filter(user_detail_id=user_id).first()
    sql=balance_calculation_function(member_dtl.id)
    earning_withdraw_data=MemberModel.objects.raw(sql)
    if earning_withdraw_data:
        earning_withdraw_data=earning_withdraw_data[0]
        print(earning_withdraw_data.total_earning)
        print(earning_withdraw_data.total_balance)
    if request.method == "POST":
        form = WithdrawForm(request.POST)
        if form.is_valid():  # Ensure the form is validated
            if earning_withdraw_data.total_balance >= form.cleaned_data['withdraw_amount']: 
                data = form.save(commit=False)
                data.member_id = user_id
                data.created_at = timezone.now()
                data.save()  
            else:
                messages.error(request, "Insufficient balance to withdraw the specified amount.")
        else:
            # Handle form errors
            messages.error(request, "Invalid form submission.")
        
    return render(request,'earning_withrew.html',{'form':form})


def side_master_list(request):
    records= SideModel.objects.filter(status=1)
    return render(request,'side_master_list.html',{'records':records})

def side_master_manage(request, action, id=None):
    if action == "update":
        record = get_object_or_404(SideModel, id=id)
        form = SideForm(request.POST or None, instance=record)
    else:
        form = SideForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        form_instance = form.save(commit=False)
        form_instance.created_at = timezone.now()
        form_instance.save()
        messages.success(request, "Data Saved")
        return redirect('/side_master_list')

    return render(request, 'side_master_manage.html', {'form': form})


def plot_master_list(request):
    records= PlotDetailsModel.objects.filter(status=1)
    return render(request,'plot_master_list.html',{'records':records})

def plot_master_manage(request, action, id=None):
    if action == "update":
        record = get_object_or_404(PlotDetailsModel, id=id)
        form = PlotDetailsForm(request.POST or None, instance=record)
    else:
        form = PlotDetailsForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        form_instance = form.save(commit=False)
        form_instance.created_at = timezone.now()
        form_instance.save()
        messages.success(request, "Data Saved")
        return redirect('/plot_master_list')
    return render(request, 'plot_master_manage.html', {'form': form})

# @csrf_exempt  # Only use this for testing; remove in production
def fetch_plot_details_by_side(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)  # Parse JSON request body
            side_id = data.get('side_id')  # Get side_id

            print("Received side_id:", side_id)  # Debugging

            plot_data = PlotDetailsModel.objects.filter(side_id=side_id).values('id', 'plot_no')

            if plot_data.exists():
                return JsonResponse({'status': 'success', 'plot_data': list(plot_data)})
            else:
                return JsonResponse({'status': 'error', 'message': 'No plots found'}, status=404)

        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON data'}, status=400)

    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)
    