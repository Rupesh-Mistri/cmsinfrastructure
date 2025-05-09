from django import forms
from django.contrib.auth.forms import UserCreationForm,AuthenticationForm
from .models import *


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ('email', 'name', 'address', 
                #   'memberID', 
                  'phone_number')

    def __init__(self, *args, **kwargs):
        super(CustomUserCreationForm, self).__init__(*args, **kwargs)

        self.fields['email'].widget = forms.EmailInput(attrs={
            'class': 'form-control',
            # 'placeholder': 'Enter your email',
        })
        self.fields['name'].widget = forms.TextInput(attrs={
            'class': 'form-control',
            # 'placeholder': 'Enter your name',
        })
        self.fields['address'].widget = forms.Textarea(attrs={
            'class': 'form-control',
            # 'placeholder': 'Enter your address',
            'rows': 3,
        })
        # self.fields['area'].widget = forms.TextInput(attrs={
        #     'class': 'form-control',
        #     'placeholder': 'Enter your area',
        # })
        # self.fields['memberID'].widget = forms.TextInput(attrs={
        #     'class': 'form-control',
        #     # 'placeholder': 'Enter your Member ID',
        # })
        self.fields['phone_number'].widget = forms.TextInput(attrs={
            'class': 'form-control',
            # 'placeholder': 'Enter your phone number',
            'maxlength':'10',
        })
        self.fields['password1'].widget = forms.PasswordInput(attrs={
            'class': 'form-control',
            # 'placeholder': 'Enter your password',
        })
        self.fields['password2'].widget = forms.PasswordInput(attrs={
            'class': 'form-control',
            # 'placeholder': 'Confirm your password',
        })

        # Optional custom labels
        self.fields['password1'].label = 'Password'
        self.fields['password2'].label = 'Confirm Password'



class CustomAuthenticationForm(AuthenticationForm):
    class Meta:
        model = CustomUser

    def __init__(self, *args, **kwargs):
        super(CustomAuthenticationForm, self).__init__(*args, **kwargs)
        self.fields['username'].widget = forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter  Member ID, or phone number',
        })
        self.fields['password'].widget = forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your password',
        })

        self.fields['username'].label = 'Mobile No. / Member ID'
        self.fields['password'].label = 'Confirm Password'




class MemberModelForm(forms.ModelForm):
    class Meta:
        model = MemberModel
        exclude = ['name','address','created_at','updated_at','status','user_detail','sponser_member','rank']
    
    def __init__(self, *args, **kwargs):
        super(MemberModelForm, self).__init__(*args, **kwargs)
        
        # Add custom widgets if needed
        # self.fields['user_detail'].widget = forms.Select(attrs={'class': 'form-control'})
        self.fields['sponserID'].widget = forms.TextInput(attrs={'class': 'form-control'})
        self.fields['sponsorName'].widget = forms.TextInput(attrs={'class': 'form-control'})
        # self.fields['sponser_member'].widget = forms.Select(attrs={'class': 'form-control'})
        # self.fields['name'].widget = forms.TextInput(attrs={'class': 'form-control'})
        self.fields['adhar_no'].widget = forms.TextInput(attrs={'class': 'form-control'})
        self.fields['pan_no'].widget = forms.TextInput(attrs={'class': 'form-control'})
        # self.fields['address'].widget = forms.Textarea(attrs={'class': 'form-control'})
        self.fields['state'].widget = forms.TextInput(attrs={'class': 'form-control'})
        self.fields['city'].widget = forms.TextInput(attrs={'class': 'form-control'})
        self.fields['pincode'].widget = forms.TextInput(attrs={'class': 'form-control'})
        self.fields['registration_fee'].widget = forms.NumberInput(attrs={'class': 'form-control'})
        
        # Add labels if needed
        # self.fields['name'].label = 'Member Name'
        # self.fields['address'].label = 'Member Address'

        state_choices = [(data.name, data.name) for data in StateModel.objects.filter(status=1)]
        self.fields['state'] = forms.ChoiceField(
            choices=[('', 'Select')] + state_choices,
            required=False,
            widget=forms.Select(attrs={
                'class': 'form-control',
                # 'style': 'border: 2px solid #a5d7c8;',
                'onchange': "handleDropdownChange(this, 'id_city', '/cascade_ajax/', 'state')"
            })
        )
        city_choices = [(data.name, data.name) for data in CityModel.objects.filter(status=1)]
        self.fields['city'] = forms.ChoiceField(
            choices=[('', 'Select')] + city_choices,
            required=False,
            widget=forms.Select(attrs={
                'class': 'form-control',
                # 'style': 'border: 2px solid #a5d7c8;',
                # 'onchange': "handleDropdownChange(this, 'id_block', '/cascade_ajax/', 'district')"
            })
        )


class PlotDetailsForm(forms.ModelForm):
    class Meta:
        model = PlotDetailsModel
        fields = [
            'plot_no',
            # 'khatiyan_document', 'khatiyan_receipt', 'village_map', 'trace_map', 
            'plot_address', 'plot_image', 'plot_video', 
            # 'mouja_name', 
            'status'
        ]

        widgets = {
            'plot_no': forms.TextInput(attrs={'class': 'form-control'}),
            # 'village_map': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            # 'trace_map': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'plot_address': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            # 'mouja_name': forms.TextInput(attrs={'class': 'form-control'}),
            # 'khatiyan_document': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            # 'khatiyan_receipt': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'plot_image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'plot_video': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
        }
        


class PurchaserDetailsForm(forms.ModelForm):
    class Meta:
        model = PurchaserDetailsModel
        fields = [
            # 'member_id', 
            'purchaser_name', 'phone_no', 'address', 
            #'address_document', 
            'purchaser_photo', 'aadhar_card_no', 
            'pan_no',  
            # 'amount_paid', 
            # 'status',
            # 'plot_id',
            
        ]


        widgets = {
            # 'member_id': forms.Select(attrs={'class': 'form-control'}),
            'purchaser_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter purchaser name'}),
            'phone_no': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter phone number'}),
            'address': forms.Textarea(attrs={'rows': 1, 'class': 'form-control', 'placeholder': 'Enter address'}),
            # 'address_document': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'purchaser_photo': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'aadhar_card_no': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Aadhar card number'}),
            'pan_no': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter PAN number'}),
            # 'plot_id': forms.Select(attrs={'class': 'form-control'}),
            # 'amount_paid': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter amount paid'}),
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)  # Call the parent constructor
        plot_choices = [(data.id, data.plot_no) for data in PlotDetailsModel.objects.filter(status=1)]
        self.fields['plot_dtl'] = forms.ChoiceField(label='Plot',
            choices=[('', 'Select')] + plot_choices,
            required=False,
            widget=forms.Select(attrs={
                'class': 'form-control',
                # 'style': 'border: 2px solid #a5d7c8;',
                # 'onchange': "handleDropdownChange(this, 'id_block', '/cascade_ajax/', 'district')"
            })
        )

    def clean_phone_no(self):
        phone_no = self.cleaned_data.get('phone_no')
        if not phone_no.isdigit() or len(phone_no) != 10:
            raise forms.ValidationError("Phone number must be a 10-digit number.")
        return phone_no

    def clean_aadhar_card_no(self):
        aadhar_card_no = self.cleaned_data.get('aadhar_card_no')
        if not aadhar_card_no.isdigit() or len(aadhar_card_no) != 12:
            raise forms.ValidationError("Aadhar card number must be a 12-digit number.")
        return aadhar_card_no

    def clean_pan_no(self):
        pan_no = self.cleaned_data.get('pan_no')
        if len(pan_no) != 10 or not pan_no.isalnum():
            raise forms.ValidationError("PAN number must be exactly 10 alphanumeric characters.")
        return pan_no

    def clean_amount_paid(self):
        amount_paid = self.cleaned_data.get('amount_paid')
        if amount_paid <= 0:
            raise forms.ValidationError("Amount paid must be greater than zero.")
        return amount_paid


class PlotBookingDetailsForm(forms.ModelForm):
   
    class Meta:
        model = PlotBookingDetailsModel
        fields = [#'member', 
                  #'purchaser_detail', 
                  #'land_detail', 
                  'no_of_decimil', 'price', 'total_amount','booking_amount',]
        widgets = {
            # 'member': forms.Select(attrs={'class': 'form-control'}),
            # 'purchaser_detail': forms.Select(attrs={'class': 'form-control'}),
            # 'land_detail': forms.Select(attrs={'class': 'form-control'}),
            'no_of_decimil': forms.NumberInput(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'total_amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'booking_amount': forms.NumberInput(attrs={'class': 'form-control','step': '0.01','readonly':'readonly' }),

        }
    def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            side_choices = [(s.id, str(s)) for s in SideModel.objects.filter(status=1)]
            # Set the default empty choice
            side_choices.insert(0, ("", "Select Side"))
            # Assign choices to the field
            self.fields['side'] = forms.ChoiceField(choices=side_choices, widget=forms.Select(attrs={'class': 'form-control'}))

    def clean_total_amount(self):
        price = self.cleaned_data.get('price')
        no_of_decimil = self.cleaned_data.get('no_of_decimil')
        total_amount = price * no_of_decimil  # Calculate total amount
        return total_amount
    
    def clean_booking_amount(self):
        price = self.cleaned_data.get('price')
        no_of_decimil = self.cleaned_data.get('no_of_decimil')
        total_amount = price * no_of_decimil  # Calculate total amount
        booking_amt= (total_amount*20)/100
        return booking_amt
    

class WithdrawForm(forms.ModelForm):
    class Meta:
        model = WithdrawModel
        fields = ['withdraw_amount','bank_account_no','ifsc_code','bank_name']
        widgets={
            'withdraw_amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'bank_account_no': forms.TextInput(attrs={'class': 'form-control', }),
            'ifsc_code': forms.TextInput(attrs={'class': 'form-control', }),
            'bank_name': forms.TextInput(attrs={'class': 'form-control', }),
        }

        # def __init__(self, *args, **kwargs):
        #     super(WithdrawForm, self).__init__(*args, **kwargs)

class PlotEmiPaymentForm(forms.ModelForm):
    class Meta:
        model = PlotEmiPaymentModel
        fields = ['installment_amount',
                #   'bank_account_no','ifsc_code','bank_name'
                  ]
        widgets={
            'installment_amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            # 'bank_account_no': forms.NumberInput(attrs={'class': 'form-control', }),
            # 'ifsc_code': forms.NumberInput(attrs={'class': 'form-control', }),
            # 'bank_name': forms.NumberInput(attrs={'class': 'form-control', }),
        }

        label={
            'installment_amount':"installment_amount"
        }

class SideForm(forms.ModelForm):
    class Meta:
        model = SideModel
        fields=['side_name']
        widgets={
            'side_name':forms.TextInput(attrs={'class': 'form-control', })
        }


class PlotDetailsForm(forms.ModelForm):
    class Meta:
        model = PlotDetailsModel
        fields=['plot_no','side']
        widgets={
            'plot_no':forms.TextInput(attrs={'class': 'form-control', }),
            'side':forms.Select(attrs={'class': 'form-control', })
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        print(self.fields['side'])
        self.fields['side'].empty_label = "Select"  # Changes default option text