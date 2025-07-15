from django.shortcuts import *
from django.contrib.auth import authenticate, login, logout
from .forms import UserSignupForm,AdminSignupForm, DonorForm, VolunteerForm
from .models import *
from django.contrib import messages
from django.contrib.auth.hashers import make_password
from django.contrib.messages import get_messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.decorators.csrf import csrf_exempt  

import datetime, hashlib


# Create your views here.
def index(request):
    return render(request, 'index.html')
# def signup_donor(request):
    
# ___________________________Signup function______________________#

def signup_donor(request):
    if request.method == 'POST':
        user_form = UserSignupForm(request.POST)
        profile_form = DonorForm(request.POST, request.FILES)

        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save(commit=False)
            # user.set_password(user_form.cleaned_data['password'])
            password = user_form.cleaned_data.get('password')
            user.set_password(password)
            user.save()

            profile = profile_form.save(commit=False)
            profile.user = user
            profile.save()

            new_user = authenticate(username=user.username, password=password)
            # new_user = authenticate(username=user.username, password=user_form.cleaned_data['password'])
            if new_user is not None:
                login(request, new_user)
                return redirect('donor_dashboard')
            else:
                print("Authentication failed")
        else:
            print("User form errors:", user_form.errors)
            print("Profile form errors:", profile_form.errors)
    else:
        user_form = UserSignupForm()
        profile_form = DonorForm()

    return render(request, 'signup.html', {'user_form': user_form, 'profile_form': profile_form})

def login_views(request):
    return render(request,'login.html')

def donor_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f"Welcome back, {user.username}!")
            return redirect('donor_dashboard')
        else:
            messages.error(request, 'Invalid username or password.')

    return render(request, 'donorlogin.html')

##########################-> the function is used for payment method
def generate_secure_hash(data, integrity_salt):
    sorted_keys = sorted(data.keys())
    hash_string = integrity_salt
    for key in sorted_keys:
        hash_string += f"&{data[key]}"

@login_required
def donor_dashboard(request):
    if request.method == 'POST':
        # Handle base fields
        donation_types = request.POST.getlist('donation_type')
        image = request.FILES.get('donation_image')
        address = request.POST.get('collection_address')
        description = request.POST.get('description')

        # New: For "Money" donation
        amount = request.POST.get('amount')
        payment_method = request.POST.get('payment_method')

        # Create donation object
        donation = Donation(
            donor=request.user,
            donation_type=', '.join(donation_types),
            donation_image=image,
            collection_address=address,
            description=description,
        )

        # If "Money" was selected
        if 'Money' in donation_types:
            donation.amount = amount
            donation.payment_method = payment_method

            if payment_method in ['JazzCash', 'EasyPaisa']:
                # Generate Transaction ID
                txn_ref = f"TXN{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
                donation.transaction_id = txn_ref
                donation.save()

                # JazzCash or EasyPaisa Integration
                post_data = {
                    'pp_Version': '1.1',
                    'pp_TxnType': 'MWALLET',
                    'pp_Language': 'EN',
                    'pp_MerchantID': 'YOUR_MERCHANT_ID',
                    'pp_Password': 'YOUR_PASSWORD',
                    'pp_TxnRefNo': txn_ref,
                    'pp_Amount': str(int(float(amount) * 100)),
                    'pp_TxnDateTime': datetime.datetime.now().strftime('%Y%m%d%H%M%S'),
                    'pp_BillReference': 'Khairunas Donation',
                    'pp_Description': 'Money Donation',
                    'pp_ReturnURL': 'http://127.0.0.1:8000/payment_callback/',
                }

                # Secure Hash
                integrity_salt = 'YOUR_INTEGRITY_SALT'
                hash_string = integrity_salt
                for key in sorted(post_data.keys()):
                    hash_string += f"&{post_data[key]}"
                post_data['pp_SecureHash'] = hashlib.sha256(hash_string.encode()).hexdigest()

                return render(request, 'payment_files/redirect_to_jazzcash.html', {'post_data': post_data})

            elif payment_method == 'Meezan Bank':
                donation.payment_status = "Manual Confirmation Needed"
                donation.save()
                return render(request, 'payment_files/meezan_instructions.html', {'donation': donation})

        # For non-money donations
        donation.save()
        return redirect('donation_success')  # Replace with your actual success page

    return render(request, 'donor_dashboard.html')


@csrf_exempt
def payment_callback(request):
    if request.method == 'POST':
        txn_ref = request.POST.get('pp_TxnRefNo')
        response_code = request.POST.get('pp_ResponseCode')

        donation = Donation.objects.filter(transaction_id=txn_ref).first()
        if donation:
            if response_code == '000':
                donation.payment_status = 'Paid'
                donation.status = 'Confirmed'
            else:
                donation.payment_status = 'Failed'
            donation.save()
        return render(request, 'payment_files/payment_result.html', {'donation': donation})


# def donor_dashboard(request):
#     if request.method == 'POST':
#         donation_types = request.POST.getlist('donation_type')  # Handles multiple checkboxes
#         donation_image = request.FILES.get('donation_image')
#         collection_address = request.POST.get('collection_address')
#         description = request.POST.get('description')

#         Donation.objects.create(
#             donor=request.user,
#             donation_type=", ".join(donation_types),
#             donation_image=donation_image,
#             collection_address=collection_address,
#             description=description
#         )
#         messages.success(request, "Your donation successfully added.")
#         return redirect('donor_dashboard')  # or redirect to a thank-you page   

#     return render(request, 'donor_dashboard.html')


def donate_now(request):
    if not request.user.is_authenticated:
        return redirect("donor_login")
    

# Admin function part ################################################################
@user_passes_test(lambda u: u.is_superuser)
def admin_profile(request):
    try:
        adminprofile = Adminprofile.objects.get(user=request.user)
        return render(request, 'admin_profile.html', {'adminprofile': adminprofile})
    except Adminprofile.DoesNotExist:
        messages.error(request, "Admin profile not found.")
        return redirect('admin_dashboard')

def admin_signup_view(request):
    if request.method == 'POST':
        form = AdminSignupForm(request.POST, request.FILES)
        if form.is_valid():
            # Create user
            user = User.objects.create(
                username=form.cleaned_data['username'],
                email=form.cleaned_data['email'],
                password=make_password(form.cleaned_data['password']),
                is_staff=True  # Make user an admin
            )
            # Create Adminprofile linked to user
            Adminprofile.objects.create(
                user=user,
                contact=form.cleaned_data['contact'],
                address=form.cleaned_data['address'],
                adminpic=form.cleaned_data['adminpic']
            )
            messages.success(request, 'Admin account created successfully!')
            return redirect('login')
    else:
        form = AdminSignupForm()
    return render(request, 'admin_signup.html', {'form': form})

def admin_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            if user.is_superuser:  # ensure only admin can login
                login(request, user)
                messages.success(request, f"Welcome back, {user.username}!")
                return redirect('admin_dashboard')
            else:
                messages.error(request, 'Access denied. Admins only.')
        else:
            messages.error(request, 'Invalid username or password.')

    return render(request, 'admin_login.html')  # make sure this template exists


def admin_dashboard(request):
    comment = request.session.get('comment')
    if comment:
        del request.session['comment']
    return render(request, 'admin_dashboard.html', {'comment': comment})
    # return render(request, 'admin_dashboard.html')

def submit_comment(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('message')

        request.session['comment'] = f"Name: {name}, Email: {email}, Message: {message}"
        return redirect('index')  # <-- fixed
  
    
@login_required(login_url='admin_login')  # Replace 'login' with your login view name
def donation_history(request):
    donations = Donation.objects.filter(donor=request.user).order_by('-submitted_at')
    return render(request, 'donation_history.html', {'donations': donations})

    
def view_detail(request, donation_id):
    # Get only donations with status 'Pending'
    donation = get_object_or_404(Donation, id=donation_id, status='Pending')

    try:
        donor_profile = Donor.objects.get(user=donation.donor)
    except Donor.DoesNotExist:
        donor_profile = None

    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status == 'Rejected':
            donation.delete()  # Delete rejected donations
        elif new_status == 'Accepted':
            donation.status = 'Accepted'
            donation.save()
        return redirect('donation_history')

    return render(request, 'view_detail.html', {
        'donation': donation,
        'donor_profile': donor_profile
    })
# @login_required
# def accepted_donation(request):
#     donations = Donation.objects.filter(status='Accepted')
#     return render(request, 'accepted_donation.html', {'donations': donations})

@login_required
def accepted_donation(request):
    if request.user.is_superuser:
        # Only admin
        donations = Donation.objects.filter(status='Accepted')
        context = {
            'donations': donations,
            'base_template': 'admin_base.html'
        }
        return render(request, 'accepted_donation.html', context)

    elif Donor.objects.filter(user=request.user).exists():
        # Only donor
        donor_profile = Donor.objects.get(user=request.user)
        donations = Donation.objects.filter(status='Accepted', donor=request.user)
        context = {
            'donations': donations,
            'base_template': 'base.html',
            'donor_profile': donor_profile
        }
        return render(request, 'accepted_donation.html', context)

    else:
        messages.error(request, "Unauthorized access.")
        return redirect('index')  # or any fallback




def donation_area(request):
    if request.method == 'POST':
        areaname = request.POST.get('areaname')
        description = request.POST.get('description')
        volunteer_ids = request.POST.getlist('volunteers')

        area = DonationArea.objects.create(
            areaname=areaname,
            description=description,
        )
        area.volunteers.set(volunteer_ids)  # Assign selected volunteers
        return redirect('manage_area')

    approved_volunteers = Volunteer.objects.filter(status='Approved').order_by('user__username')
    return render(request, 'donation_area.html', {
        'edit': False,
        'approved_volunteers': approved_volunteers,
    })

def manage_area(request):
    areas = DonationArea.objects.prefetch_related('volunteers').all()
    return render(request, 'manage_area.html', {'areas': areas})


def manage_donor(request):
    donors = Donor.objects.all().order_by('-regdate')  # You can change the order if needed
    return render(request, 'manage_donor.html', {'donors': donors})

def donor_detail(request, donor_id):
    donor = get_object_or_404(Donor, id=donor_id)

    if request.method == 'POST':
        contact = request.POST.get('contact')
        userpic = request.FILES.get('userpic')

        donor.contact = contact
        if userpic:
            donor.userpic = userpic
        donor.save()

        messages.success(request, "Donor details updated successfully.")
        return redirect('manage_donor')  # ✅ Redirects to manage_donor after update

    return render(request, 'donor_detail.html', {'donor': donor})

# volunteer function part #################################################################
def volunter_signup(request):
    if request.method == 'POST':
        user_form = UserSignupForm(request.POST)
        profile_form = VolunteerForm(request.POST, request.FILES)

        if user_form.is_valid() and profile_form.is_valid():
            username = user_form.cleaned_data['username'].strip()

            # Problem 1 Fix: accurate username check
            if User.objects.filter(username__iexact=username).exists():
                messages.error(request, "This username already exists.")
                return redirect('volunter_signup')

            # Create user (but don't log in yet)
            user = user_form.save(commit=False)
            user.username = username  # update trimmed username
            user.set_password(user_form.cleaned_data['password'])
            user.save()

            # Create volunteer profile with status Pending
            volunteer = profile_form.save(commit=False)
            volunteer.user = user
            volunteer.status = 'Pending'  # Problem 2 Fix
            volunteer.save()

            messages.success(request, "Your account has been created and is pending approval.")
            return redirect('volunteer_login')  # No login here

        else:
            print("User form errors:", user_form.errors)
            print("Volunteer form errors:", profile_form.errors)

    else:
        user_form = UserSignupForm()
        profile_form = VolunteerForm()

    return render(request, 'volunter_signup.html', {
        'user_form': user_form,
        'profile_form': profile_form
    })


# def volunter_signup(request):
#     if request.method == 'POST':
#         user_form = UserSignupForm(request.POST)
#         profile_form = VolunteerForm(request.POST, request.FILES)

#         if user_form.is_valid() and profile_form.is_valid():
#             username = user_form.cleaned_data['username']
            
#             # Check if user already exists
#             if User.objects.filter(username=username).exists():
#                 messages.error(request, "This username already exists. Please try another.")
#                 return redirect('volunter_signup')

#             # Create user
#             user = user_form.save(commit=False)
#             user.set_password(user_form.cleaned_data['password'])
#             user.save()

#             # Create volunteer profile
#             volunteer = profile_form.save(commit=False)
#             volunteer.user = user
#             volunteer.status = 'Pending'  # ✅ explicitly set status
#             volunteer.save()

#             # Log in and redirect to dashboard
#             login(request, user)
#             return redirect('volunter_dashboard')

#         else:
#             # Debug: print form errors if any
#             print("User form errors:", user_form.errors)
#             print("Volunteer form errors:", profile_form.errors)

#     else:
#         user_form = UserSignupForm()
#         profile_form = VolunteerForm()

#     return render(request, 'volunter_signup.html', {
#         'user_form': user_form,
#         'profile_form': profile_form
#     })

def volunteer_login(request):
    if request.method == "GET":
        list(get_messages(request)) 
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        # First, try to authenticate the user
        user = authenticate(request, username=username, password=password)
        if user is None:
            messages.error(request, "Invalid username or password.")
            return redirect('volunteer_login')

        # Check if the user has a volunteer profile
        volunteer = Volunteer.objects.filter(user=user).first()
        if not volunteer:
            messages.error(request, "You are not registered as a volunteer.")
            return redirect('volunteer_login')

        # Check the approval status
        if volunteer.status != 'Approved':
            messages.error(request, "Your account is not approved yet. Please wait for admin approval.")
            return redirect('volunteer_login')

        # Everything’s good → log them in
        login(request, user)
        return redirect('volunter_dashboard')

    # GET request
    return render(request, 'volunteer_login.html')

# function for profile page 


def volunteer_profile(request):
    try:
        volunteer = Volunteer.objects.get(user=request.user)
        return render(request, 'volunteer_profile.html', {'volunteer': volunteer})
    except Volunteer.DoesNotExist:
        messages.error(request, "Volunteer profile not found.")
        return redirect('volunter_dashboard')
def edit_profile(request):
    # Update common User fields
    if request.method == 'POST':
        request.user.first_name = request.POST.get('first_name')
        request.user.email = request.POST.get('email')
        request.user.save()

        # If superuser → update Adminprofile
        if request.user.is_superuser:
            try:
                adminprofile = Adminprofile.objects.get(user=request.user)
            except Adminprofile.DoesNotExist:
                messages.error(request, "Admin profile not found.")
                return redirect('profile')

            adminprofile.contact = request.POST.get('contact')
            adminprofile.address = request.POST.get('address')

            if request.FILES.get('adminpic'):
                adminprofile.adminpic = request.FILES['adminpic']

            adminprofile.save()
            messages.success(request, 'Admin profile updated successfully!')
            return redirect('profile')

        # Else update Volunteer profile
        else:
            try:
                volunteer = request.user.volunteer
            except Volunteer.DoesNotExist:
                messages.error(request, "Volunteer profile not found.")
                return redirect('profile')

            volunteer.contact = request.POST.get('contact')
            volunteer.address = request.POST.get('address')

            if request.FILES.get('volunteerpic'):
                volunteer.volunteerpic = request.FILES['volunteerpic']

            volunteer.save()
            messages.success(request, 'Volunteer profile updated successfully!')
            return redirect('profile')

    # GET request — load the appropriate form/template
    if request.user.is_superuser:
        adminprofile = Adminprofile.objects.get(user=request.user)
        return render(request, 'edit_admin_profile.html', {
            'adminprofile': adminprofile
        })
    else:
        volunteer = request.user.volunteer
        return render(request, 'edit_volunter_profile.html', {
            'volunteer': volunteer
        })

# @login_required
# def edit_volunter_profile(request):
#     volunteer = request.user.volunteer

#     if request.method == 'POST':
#         # Update User model
#         request.user.first_name = request.POST.get('first_name')
#         request.user.email = request.POST.get('email')
#         request.user.save()

#         # Update Volunteer model
#         volunteer.contact = request.POST.get('contact')
#         volunteer.address = request.POST.get('address')

#         if request.FILES.get('volunteerpic'):
#             volunteer.volunteerpic = request.FILES['volunteerpic']

#         volunteer.save()
#         messages.success(request, 'Profile updated successfully!')
#         return redirect('profile')

#     return render(request, 'edit_volunter_profile.html', {
#         'volunteer': volunteer
#     })


@login_required
def volunter_dashboard(request):
    volunteer = Volunteer.objects.filter(user=request.user).first()

    return render(request, 'volunter_dashboard.html', {
        'volunteer': volunteer
    })
def new_volunter(request):
    volunters = Volunteer.objects.filter(status='pending').exclude(id=None).order_by('-regdate')

    return render(request, 'new_volunter.html', {
        'volunters': volunters
    })


def volunter_detail(request, volunteer_id):
    volunteer = get_object_or_404(Volunteer, id=volunteer_id)

    if request.method == 'POST':
        contact = request.POST.get('contact')
        userpic = request.FILES.get('userpic')
        status = request.POST.get('status')  # ✅ Capture status from the form

        volunteer.contact = contact
        if userpic:
            volunteer.userpic = userpic
        if status:
            volunteer.status = status

        volunteer.save()
        messages.success(request, "Volunteer details updated successfully.")
        return redirect('new_volunter')  # ✅ Redirects to the volunteer list page

    return render(request, 'volunter_detail.html', {'volunteer': volunteer})

def approved_volunter(request):
    volunteers = Volunteer.objects.filter(status='Approved')
    return render(request, 'approved_volunter.html', {'volunteers': volunteers})

def new_donation_request(request):
    volunteer = Volunteer.objects.get(user=request.user)

    # Get list of accepted donation area IDs from session
    accepted_ids = request.session.get('accepted_area_ids', [])

    if request.method == 'POST':
        area_id = request.POST.get('area_id')
        action = request.POST.get('response')

        try:
            area = DonationArea.objects.get(id=area_id)

            if action == 'accepted':
                # ✅ Save the accepted area ID to session
                accepted_ids.append(area.id)
                request.session['accepted_area_ids'] = accepted_ids
                messages.success(request, f"You accepted the donation request for '{area.areaname}'.")
                return redirect('vol_donation_histry')

            elif action == 'rejected':
                area.volunteers.remove(volunteer)
                messages.error(request, f"You rejected the donation request for '{area.areaname}'.")
                return redirect('new_donation_request')

        except DonationArea.DoesNotExist:
            messages.error(request, "Area not found.")

    # ✅ Show only areas assigned and not accepted yet
    requests = DonationArea.objects.filter(volunteers=volunteer).exclude(id__in=accepted_ids)

    return render(request, 'new_donation_request.html', {'requests': requests})

@login_required
def vol_donation_histry(request):
    if not hasattr(request.user, 'volunteer'):
        messages.error(request, "Access denied. Only volunteers can view this page.")
        return redirect('index')

    volunteer = request.user.volunteer

    # ✅ Get accepted donation area IDs from session
    accepted_ids = request.session.get('accepted_area_ids', [])

    # ✅ Fetch accepted DonationArea objects
    areas = DonationArea.objects.filter(id__in=accepted_ids)

    return render(request, 'vol_donation_histry.html', {
        'areas': areas,
        'user': request.user,
    })



# common function  for all ##################################################

def add_beneficiaries(request):
    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        father_name = request.POST.get('father_name')
        contact_number = request.POST.get('contact_number')
        cnic = request.POST.get('cnic')
        family_members = request.POST.get('family_members')
        status = request.POST.get('status')
        address = request.POST.get('address')

        # Save to DB
        Beneficiary.objects.create(
            full_name=full_name,
            father_name=father_name,
            contact_number=contact_number,
            cnic=cnic,
            family_members=family_members,
            status=status,
            address=address
        )

        return redirect('beneficiaries')  # Redirect to the table page
    base_template = 'admin_base.html' if request.user.is_superuser else 'volunter_base.html'

    return render(request, 'add_beneficiaries.html', {
        'base_template': base_template
    })

    # if request.user.is_superuser:
    #     base_template = 'admin_base.html'
    # else:
    #     base_template = 'volunter_base.html'

    # return render(request, 'add_beneficiaries.html', {
    #     'base_template': base_template
    # })
    # return render(request, 'add_beneficiaries.html')

@login_required
def beneficiaries(request):
    beneficiaries = Beneficiary.objects.all()

    if request.user.is_superuser:
        return render(request, 'share_beneficiant/beneficiaries_admin.html', {
            'beneficiaries': beneficiaries
        })
    else:
        return render(request, 'share_beneficiant/beneficiaries_volunter.html', {
            'beneficiaries': beneficiaries
        })
# def beneficiaries(request):
#     beneficiaries = Beneficiary.objects.all().order_by('-id')
#     return render(request, 'beneficiaries.html', {
#         'beneficiaries': beneficiaries
#     })

def edit_item(request, model_name, item_id):
    if model_name == 'area':
        area = get_object_or_404(DonationArea, id=item_id)
        volunteers = Volunteer.objects.all()

        if request.method == 'POST':
            area.areaname = request.POST.get('areaname')
            area.description = request.POST.get('description')
            area.save()

            selected_volunteers = request.POST.getlist('volunteers[]')
            area.volunteers.set(selected_volunteers)

            return redirect('manage_area')

        return render(request, 'edit_area.html', {
            'edit': True,
            'area': area,
            'volunteers': volunteers,
        })
    elif model_name == 'beneficiary':
        item = get_object_or_404(Beneficiary, id=item_id)

        if request.method == 'POST':
            item.full_name = request.POST.get('full_name')
            item.full_name = request.POST.get('father_name')
            item.contact_number = request.POST.get('contact_number')
            item.cnic = request.POST.get('cnic')
            item.family_members = request.POST.get('family_members')
            item.full_name = request.POST.get('status')
            item.address = request.POST.get('address')
            item.save()
            return redirect('beneficiaries')

        return render(request, 'edit_beneficiary.html', {
            'edit': True,
            'beneficiary': item
        })

    elif model_name == 'volunteer':
        item = get_object_or_404(Volunteer, id=item_id)

        if request.method == 'POST':
            item.contact = request.POST.get('contact')
            item.address = request.POST.get('address')
            item.aboutme = request.POST.get('aboutme')
            userpic = request.FILES.get('userpic')
            if userpic:
                item.userpic = userpic
            item.save()
            return redirect('approved_volunter')

        return render(request, 'edit_volunter.html', {
            'edit': True,
            'volunteer': item
        })

    else:
        return redirect('index')  # fallback if model_name not matched


def delete_item(request, model_name, item_id):
    if request.method == 'POST':
        if model_name == 'area':
            obj = get_object_or_404(DonationArea, id=item_id)
            redirect_url = 'manage_area'
        elif model_name == 'donor':
            obj = get_object_or_404(Donor, id=item_id)
            redirect_url = 'manage_donor'

        elif model_name == 'beneficiary':
            obj = get_object_or_404(Beneficiary, id=item_id)
            redirect_url = 'beneficiaries'
            
        elif model_name == 'volunteer':
            try:
                obj = Volunteer.objects.get(id=item_id)
                redirect_url = 'approved_volunter'
            except Volunteer.DoesNotExist:
                messages.error(request, "Volunteer already deleted or not found.")
                return redirect('approved_volunter')
        else:
            return redirect('index')  # fallback

        obj.delete()
        messages.success(request, f"{model_name.capitalize()} deleted successfully.")
        return redirect(redirect_url)


def Logout_view(request):
    logout(request)
    return redirect('index')