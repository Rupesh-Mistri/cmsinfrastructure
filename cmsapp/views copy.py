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

def index(request):
    """
    Renders the homepage.
    """
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
    from .import_data import import_data_csv
    import_data_csv()
    user_detail=request.user
    user_id =user_detail.id
    print(user_id)
    user= CustomUser.objects.filter(is_active=True,id=user_id).first()
    # print(user.username)
    sql=f"""
WITH RECURSIVE
        os (id, name, sponser_member_id, rank)
        AS (
        SELECT id,
                name,
                sponser_member_id,
                rank AS rank
        FROM tbl_member
        WHERE id = {user_id}
        UNION ALL
        SELECT m.id,
                m.name,
                m.sponser_member_id,
                os.rank 
        FROM tbl_member m
        INNER JOIN os ON m.sponser_member_id = os.id
        )
        SELECT 0 as id,
        os.rank,
        COALESCE(SUM(t.total_amount),0 ) AS total_sales,
        ROUND(SUM(
            CASE
                when os.rank ='CP-01' THEN ROUND(5 * COALESCE(t.total_amount,0))/100
                when os.rank ='CP-02' THEN ROUND(7 * COALESCE(t.total_amount,0))/100
                when os.rank ='CP-03' THEN ROUND(9 * COALESCE(t.total_amount,0))/100
                when os.rank ='CP-04' THEN ROUND(11 * COALESCE(t.total_amount,0))/100
                when os.rank ='CP-05' THEN ROUND(13 * COALESCE(t.total_amount,0))/100
                when os.rank ='CP-06' THEN ROUND(14 * COALESCE(t.total_amount,0))/100
                when os.rank ='CP-07' THEN ROUND(15 * COALESCE(t.total_amount,0))/100
                when os.rank ='CP-08' THEN ROUND(16 * COALESCE(t.total_amount,0))/100
                when os.rank ='CP-09' THEN ROUND(17 * COALESCE(t.total_amount,0))/100
                when os.rank ='CP-10' THEN ROUND(18 * COALESCE(t.total_amount,0))/100 
                ELSE 0
            END
        ),2) AS total_commission
        FROM os
        LEFT JOIN tbl_plot_sell_details t ON os.id = t.member_id
        GROUP BY os.rank
        ORDER BY os.rank;
    """
    commistion_list=MemberModel.objects.raw(sql)
    # print(commistion_list)
    total_commission_earn=0
    for comms in commistion_list:
        print(comms.total_commission)
        total_commission_earn+=comms.total_commission
    # print('total_commission_earn:',total_commission_earn)
    referral_list_count= ''#CustomUser.objects.filter(member__sponser_member_id=user_id).count()
    total_member_count=''#CustomUser.objects.all().count()
    return render(request,'home.html',{'user':user,'total_commission_earn':total_commission_earn,'referral_list_count':referral_list_count,'total_member_count':total_member_count})



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
        if sponser_mber_exist:
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
                    data.sponser_member_id=sponser_mber_exist.id
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

from django.db.models import Sum


@login_req
def purchaser_detail_form(request):
    form = PurchaserDetailsForm()
    lform = PlotBookingDetailsForm()
    user_detail = request.user 
    user_id=user_detail.id
    user_details = MemberModel.objects.filter(user_detail_id=user_detail.id).first()
    # print(user_details.id)

    if request.method == "POST":
        form = PurchaserDetailsForm(request.POST, request.FILES)
        lform = PlotBookingDetailsForm(request.POST, request.FILES)

        if form.is_valid() and lform.is_valid():
            # Save PurchaserDetails first
            total_amount=float(request.POST['total_amount'])

            # total_bussiness_slab = PlotBookingDetailsModel.objects.filter(member_id=user_details.id).aggregate(total=Sum('total_amount'))['total'] or 0

            purchaser_details = form.save(commit=False)
            purchaser_details.member_id_id = user_detail.id
            purchaser_details.plot_dtl_id = request.POST['plot_dtl']
            purchaser_details.created_at = timezone.now()
            purchaser_details.updated_at = timezone.now()
            # purchaser_details.status =1
            purchaser_details.amount_paid= request.POST['total_amount']
            purchaser_details.save()

            # Save LandSellDetails next, and link to PurchaserDetails
            land_sell_details = lform.save(commit=False)
            land_sell_details.member_id = user_detail.id  # Use the logged-in user (from user_details)
            land_sell_details.purchaser_detail = purchaser_details  # Link to the saved purchaser detail
            land_sell_details.plot_dtl_id = purchaser_details.plot_dtl_id  # Assuming `land_id` is the correct field
            land_sell_details.created_at = timezone.now()
            land_sell_details.updated_at = timezone.now()
            land_sell_details.save()

            # Define the rank-business slab mapping as numeric ranges
            rank_bussiness_slab_mapping = {
                'CP-01': (0, 500000),         # 0-5 Lacs
                'CP-02': (500001, 2500000),   # 5-25 Lacs
                'CP-03': (2500001, 5000000),  # 25-50 Lacs
                'CP-04': (5000001, 10000000), # 50 Lacs - 1 Crore
                'CP-05': (10000001, 50000000),# 1-5 Crores
                'CP-06': (50000001, 100000000),# 5-10 Crores
                'CP-07': (100000001, 250000000),# 10-25 Crores
                'CP-08': (250000001, 500000000),# 25-50 Crores
                'CP-09': (500000001, 750000000),# 50-75 Crores
                'CP-10': (750000001, 1000000000),# 75-100 Crores
            }

            # Calculate the total business slab for the user
            total_bussiness_slab = PlotBookingDetailsModel.objects.filter(
                member_id=user_details.id
            ).aggregate(total=Sum('total_amount'))['total'] or 0

            # Determine the rank based on total_bussiness_slab
            new_rank = None
            for rank, (lower_bound, upper_bound) in rank_bussiness_slab_mapping.items():
                if lower_bound <= total_bussiness_slab <= upper_bound:
                    new_rank = rank
                    break

            # Update the user's rank if a matching rank was found
            if new_rank:
                MemberModel.objects.filter(id=user_details.id).update(rank=new_rank)

            user_details = MemberModel.objects.filter(user_detail_id=user_detail.id).first()

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

            self_percentage = rank_percentage_mapping.get(user_details.rank, 0)  # Default to 0 if rank is not found
            commision_earn = round(self_percentage * total_amount/ 100)

            EarningModel.objects.create(
                type="self",
                plot_booking_detail_id=land_sell_details.id,
                earning_amount=commision_earn,
                member_id   = user_details.id
            )

            # def get_all_upliners(member):
            #     upliners = []
            #     while member.sponser_member:  # Keep going up the hierarchy
            #         member = member.sponser_member
            #         upliners.append(member)
            #     return upliners

            # Example usage
            upliners = get_all_upliners(user_id)
            for upliner in upliners:
                print(f"Upliner: {upliner.name}, ID: {upliner.id}")

                percentage = rank_percentage_mapping.get(upliner.rank, 0)  # Default to 0 if rank is not found
                percentage_difference=self_percentage-percentage

                if percentage_difference<0:
                    continue
                commision_earn = round(percentage_difference * total_amount/ 100)
                commis_create=EarningModel.objects.create(
                            type="not_self",
                            plot_booking_detail_id=1,
                            earning_amount=commision_earn,
                            member_id   = upliner.id
                        )

            print("Details Submitted Successfully")
            messages.success(request, "Details Submitted Successfully")
            return redirect(f'/plot_booking_details/booking_slip/{purchaser_details.id}')  # Redirect after success

        else:
            # Handle form errors if validation fails
            print("Form errors:", form.errors, )
            print("LForm errors:", lform.errors, )
            messages.error(request,form.errors, lform.errors)
            return render(request, 'purchaser_detail_form.html', {'form': form, 'lform': lform, 'user_details': user_details})

    return render(request, 'purchaser_detail_form.html', {'form': form, 'lform': lform, 'user_details': user_details})

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


