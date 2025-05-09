from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils.timezone import now
from django.core.exceptions import ValidationError
import hashlib
import random
import string

class CustomUserManager(BaseUserManager):
    def create_user(self, email=None, name=None, password=None, **extra_fields):
        if not email and not extra_fields.get('phone_number') and not extra_fields.get('memberID'):
            raise ValueError('At least one of Email, Phone Number, or Member ID must be set.')

        email = self.normalize_email(email) if email else None
        user = self.model(email=email, name=name, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email=email, name=name, password=password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True, null=True, blank=True)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    last_login = models.DateTimeField(null=True, blank=True)
    address = models.TextField()
    area = models.CharField(max_length=150,null=True, blank=True)
    created_at = models.DateTimeField(default=now)
    memberID = models.CharField(max_length=15, unique=True, blank=True, null=True)
    phone_number = models.CharField(max_length=15, unique=True, blank=True, null=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    def __str__(self):
        return self.email or self.phone_number or self.memberID

    class Meta:
        db_table = 'tbl_user'


class MemberModel(models.Model):
    id = models.BigAutoField(primary_key=True)
    user_detail = models.ForeignKey("CustomUser",  on_delete=models.CASCADE)
    sponserID = models.CharField(max_length=50)
    sponsorName = models.CharField(max_length=100)
    sponser_member = models.ForeignKey(
        "self",  # Self-referential ForeignKey
        # verbose_name=_("Sponsor Member"),
        on_delete=models.CASCADE,
        blank=True,  # Allows this field to be optional
        null=True    # Allows this field to accept NULL values
    )
    name = models.CharField(max_length=100,null=True, blank=True)
    # mobile_no = models.CharField(max_length=10)
    # emailaddress = models.EmailField(blank=True, null=True)
    adhar_no = models.CharField(max_length=12)
    pan_no = models.CharField(max_length=10)
    address = models.TextField(null=True, blank=True)
    state = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    pincode = models.CharField(max_length=6)
    created_at = models.DateTimeField(default=now)  # Default to current time
    updated_at = models.DateTimeField(auto_now=True)  # Automatically update on save
    status = models.IntegerField(default=1)
    rank    = models.CharField(max_length=10)
    registration_fee =models.DecimalField( max_digits=5, decimal_places=2)
    def __str__(self):
        return self.name

    class Meta:
        db_table = "tbl_member"

class StateModel(models.Model):
    id= models.BigAutoField(primary_key=True)
    name =models.CharField(max_length=100)
    # code = models.IntegerField()
    created_at = models.DateTimeField(default=now)  # Default to current time
    updated_at = models.DateTimeField(auto_now=True)  # Automatically update on save
    status = models.IntegerField(default=1)

    def __str__(self):
        return self.name
    class Meta:
        db_table="tbl_state"

class CityModel(models.Model):
    id= models.BigAutoField(primary_key=True)
    name=models.CharField(max_length=100)
    state= models.ForeignKey("StateModel", on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=now)  # Default to current time
    updated_at = models.DateTimeField(auto_now=True)  # Automatically update on save
    status = models.IntegerField(default=1)

    def __str__(self):
        return self.name
    class Meta:
        db_table="tbl_city"


class SideModel(models.Model):
    id= models.BigAutoField(primary_key=True)
    side_name = models.CharField(max_length=225)
    created_at                      = models.DateTimeField(default=now)  # Default to current time
    updated_at                      = models.DateTimeField(auto_now=True)  # Automatically update on save
    status                          = models.SmallIntegerField(default=1)
    def __str__(self):
        return self.side_name
    class Meta:
        db_table="tbl_side"

class PlotDetailsModel(models.Model):
    id                              = models.BigAutoField(primary_key=True)
    plot_no                         =models.CharField(max_length=100)
    # khatiyan_document               = models.FileField(upload_to=None, max_length=100)
    # khatiyan_receipt                = models.FileField( upload_to=None, max_length=100)
    # village_map                     = models.TextField()
    # trace_map                       = models.TextField()
    plot_address                    = models.TextField(null=True,blank=True)
    plot_image                      = models.FileField(upload_to=None, max_length=200,null=True,blank=True)
    plot_video                      = models.FileField(upload_to=None, max_length=200,null=True,blank=True)
    # mouja_name                      = models.CharField(max_length=100)   
    side                            = models.ForeignKey("SideModel", on_delete=models.CASCADE)
    created_at                      = models.DateTimeField(default=now)  # Default to current time
    updated_at                      = models.DateTimeField(auto_now=True)  # Automatically update on save
    status                          = models.SmallIntegerField(default=1)

    def __str__(self):
        return self.name
    class Meta:
        db_table="tbl_plot_details"

def address_document_name_change(instance, filename):
    random_string = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
    extension = filename.split('.')[-1]
    return f'images/address_document{instance.id}{random_string}.{extension}'
def purchaser_photo_name_change(instance, filename):
    random_string = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
    extension = filename.split('.')[-1]
    return f'images/purchaser_photo{instance.id}{random_string}.{extension}'
class PurchaserDetailsModel(models.Model):
    id                      = models.BigAutoField(primary_key=True)
    member_id               = models.ForeignKey("MemberModel",  on_delete=models.CASCADE)
    purchaser_name          = models.CharField(max_length=100)
    phone_no                = models.CharField(max_length=10)
    address                 = models.TextField()
    address_document        = models.FileField( upload_to=address_document_name_change, max_length=100 ,null=True,blank=True)
    purchaser_photo         = models.ImageField( upload_to=purchaser_photo_name_change, height_field=None, width_field=None, max_length=None)
    aadhar_card_no          = models.CharField( max_length=12)
    pan_no                  = models.CharField(max_length=10)
    plot_dtl                 = models.ForeignKey("PlotDetailsModel",  on_delete=models.CASCADE)
    amount_paid             = models.DecimalField( max_digits=10, decimal_places=2)
    created_at              = models.DateTimeField(default=now)  # Default to current time
    updated_at              = models.DateTimeField(auto_now=True)  # Automatically update on save
    status                  = models.SmallIntegerField(default=1)
    
    def __str__(self):
        return self.purchaser_name
    class Meta:
        db_table="tbl_purchaser"


class LandDistanceFromLandmark(models.Model):
    id                      = models.BigAutoField(primary_key=True)
    landmark_name           = models.CharField(max_length=100)
    distance_in_km          = models.IntegerField()
    created_at              = models.DateTimeField(default=now)  # Default to current time
    updated_at              = models.DateTimeField(auto_now=True)  # Automatically update on save
    status                  = models.SmallIntegerField(default=1)
    def __str__(self):
        return self.name
    class Meta:
        db_table="tbl_land_distance"


class PlotBookingDetailsModel(models.Model):
    id                      = models.BigAutoField(primary_key=True)
    member                  =models.ForeignKey("MemberModel", verbose_name=_(""), on_delete=models.CASCADE)
    purchaser_detail          =models.ForeignKey("PurchaserDetailsModel", verbose_name=_(""), on_delete=models.CASCADE)
    plot_dtl         = models.ForeignKey("PlotDetailsModel", verbose_name=_(""), on_delete=models.CASCADE)
    no_of_decimil        = models.IntegerField(null=False)
    price               = models.DecimalField( max_digits=10, decimal_places=2)
    total_amount        = models.DecimalField( max_digits=10, decimal_places=2)
    booking_amount          = models.DecimalField( max_digits=10, decimal_places=2)
    monthly_payment_amount   = models.DecimalField( max_digits=10, decimal_places=2)
    no_of_installment        = models.IntegerField(default=10)
    class Meta:
        db_table="tbl_plot_sell_details"


class EarningModel(models.Model):
    id                      = models.BigAutoField(primary_key=True)
    type                    = models.CharField( max_length=50)
    plot_booking_detail     = models.ForeignKey("PlotBookingDetailsModel", verbose_name=_(""), on_delete=models.CASCADE)
    earning_amount          = models.DecimalField( max_digits=15, decimal_places=2)
    member                  =models.ForeignKey("MemberModel", verbose_name=_(""), on_delete=models.CASCADE)
    class Meta:
        db_table = "tbl_earning"

class WithdrawModel(models.Model):
    id                      = models.BigAutoField(primary_key=True)
    member                  =models.ForeignKey("MemberModel", verbose_name=_(""), on_delete=models.CASCADE)
    withdraw_amount          = models.DecimalField( max_digits=15, decimal_places=2)
    bank_account_no         =models.CharField( max_length=50)
    ifsc_code               = models.CharField( max_length=50)
    bank_name               = models.CharField( max_length=50)
    created_at              = models.DateTimeField(default=now)  # Default to current time
    updated_at              = models.DateTimeField(auto_now=True)  # Automatically update on save
    status                  = models.SmallIntegerField(default=1)

    class Meta:
        db_table ="tbl_withdrawal"

class RewardModel(models.Model):
    id                      = models.BigAutoField(primary_key=True)
    member                  =models.ForeignKey("MemberModel", verbose_name=_(""), on_delete=models.CASCADE)
    reward                  =models.CharField( max_length=50)
    created_at              = models.DateTimeField(default=now)  # Default to current time
    updated_at              = models.DateTimeField(auto_now=True)  # Automatically update on save
    status                  = models.SmallIntegerField(default=1)

    class Meta:
        db_table ="tbl_reward"

class PlotEmiPaymentModel(models.Model):
    id                      = models.BigAutoField(primary_key=True)
    plot_booking_detail     = models.ForeignKey("PlotBookingDetailsModel", verbose_name=_(""), on_delete=models.CASCADE)
    installment_amount      = models.DecimalField(_(""), max_digits=10, decimal_places=2)
    member                  =models.ForeignKey("MemberModel", verbose_name=_(""), on_delete=models.CASCADE)
    created_at              = models.DateTimeField(default=now)  # Default to current time
    updated_at              = models.DateTimeField(auto_now=True)  # Automatically update on save
    class Meta:
        db_table ="tbl_emi_payment"


# alter table tbl_member add COLUMN  rank  varchar(200);

# INSERT INTO `tbl_member` (`id`, `sponserID`, `sponsorName`, `name`, `adhar_no`, `pan_no`, `address`, `state`, `city`, `pincode`, `created_at`, `updated_at`, `status`, `registration_fee`, `sponser_member_id`, `user_detail_id`, `rank`) VALUES
# (1, '', 'admin', 'Test', '123456789012', 'gd54444444', 'tst', 'Jharkhand', 'Ranchi', '654321', '2025-01-21 05:34:41.623387', '2025-01-21 05:34:41.959220', 1, 300.00, NULL, 1, 'CP-01');


# ALTER TABLE tbl_earning
# MODIFY COLUMN earning_amount DECIMAL(15,2);

"""
INSERT INTO `tbl_plot_details`(`id`, `plot_address`, `plot_image`, `plot_video`, `plot_no`, `created_at`, `updated_at`, `status`) VALUES (1,'Test','test','test','PL01',CURRENT_TIMESTAMP,CURRENT_TIMESTAMP,1)
"""