"""
Author: Peter Zujko (@zujko)
Description: Handles views and endpoints for all petition related operations.
Date Created: Sept 15 2016
Updated: Oct 26 2016
"""
from django.shortcuts import render, get_object_or_404, render, redirect
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import F
from django.utils import timezone
from petitions.models import Petition
from profile.models import Profile
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.core.mail import EmailMessage
from django.template.loader import get_template
from django.template import Context
from django.http import HttpResponse
from django.http import HttpRequest
import time

def petition(request, petition_id):
    """ Handles displaying A single petition. 
    DB queried to get Petition object and User objects.
    User object queries retrieve author
    and list of all users who signed the petition.
    """
    # Get petition of given id, if not found, display 404
    petition = get_object_or_404(Petition, pk=petition_id) 
    # Get author of the petition
    author = User.objects.get(pk=petition.author.id)
    user = request.user

    # Check if user is authenticated before querying
    curr_user_signed = user.profile.petitions_signed.filter(id=petition.id).exists() if user.is_authenticated() else None

    # Get QuerySet of all users who signed this petition
    users_signed = Profile.objects.filter(petitions_signed=petition)
    
    data_object = {
        'petition': petition,
        'current_user': user,
        'curr_user_signed': curr_user_signed,
        'users_signed': users_signed,
        'curr_user_petition': author == user
    }

    return render(request, 'petition.html', data_object)      

# ENDPOINTS #

@login_required
@require_POST
def petition_sign(request, petition_id):
    """ Endpoint for signing a petition.
    This endpoint requires the user be signed in
    and that the HTTP request method is a POST.
    """
    petition = get_object_or_404(Petition, pk=petition_id)
    user = request.user
    user.profile.petitions_signed.add(petition)
    user.save()
    petition.signatures += 1
    petition.last_signed = timezone.now()
    petition.save()
    
    return redirect('/petition/'+str(petition_id))

@login_required
@require_POST
def petition_subscribe(request, petition_id):
    """ Endpoint subscribes a user to the petition"""
    petition = get_object_or_404(Petition, pk=petition_id)
    user = request.user
    user.profile.subscriptions.add(petition)
    user.save()
    
    return redirect('petition/' + str(petition_id))

@login_required
@require_POST
@user_passes_test(lambda u: u.is_staff)
def petition_unpublish(request, petition_id):
    """ Endpoint for unpublishing a petition.
    This endpoint requires that the user be signed in,
    the HTTP request method is a POST, and that the 
    user is an admin.
    """
    petition = get_object_or_404(Petition, pk=petition_id)
    petition.published = False    
    petition.save()

    return redirect('petition/' + str(petition_id))

# HELPER FUNCTIONS #

# PETITION SORTING 
def most_recent():
    return Petition.objects.all() \
            .filter(expires__gt=timezone.now()) \
            .exclude(has_response=True) \
            .filter(published=True) \
            .order_by('-created_at')

def most_signatures():
    return Petition.objects.all() \
            .filter(expires__gt=timezone.now()) \
            .exclude(has_response=True) \
            .filter(published=True) \
            .order_by('-signatures')

def last_signed():
    return Petition.objects.all() \
            .filter(expires__gt=timezone.now()) \
            .exclude(has_response=True) \
            .filter(published=True) \
            .order_by('-last_signed')

def all_active():
    """All petitions that have no yet expired"""
    return Petition.objects.all() \
            .filter(expires__gt=timezone.now()) \
            .exclude(published=False) \
            .order_by('-created_at')

def all_inactive():
    """All petitions that have expired and are published"""
    return Petition.objects.all() \
            .filter(expires__lt=timezone.now()) \
            .exclude(published=False) \
            .order_by('-created_at')


def sendSimpleEmail(request, recipients):
    email = EmailMessage("hello paul", "<b>comment tu vas?</b>", "sgnoreply@rit.edu", [recipients])
    email.content_subtype = "html"
    res = email.send()
    return HttpResponse('%s'%res)

def sendEmail(request, recipients, petition_id, emailType):

    petition = get_object_or_404(Petition, pk=petition_id)

    if emailType == 'approved':
        email = EmailMessage(

            'Petition approved.',
            get_template('email_inlined/petition_approved.html').render(

                Context({
                    'petition_id': petition_id,
                    'title': petition.title,
                    'author': petition.author.first_name + ' ' + petition.author.last_name,
                    'site_path': request.META['HTTP_HOST'],
                    'protocol': 'https' if request.is_secure() else 'http',
                    'timestamp': time.strftime('[%H:%M:%S %d/%m/%Y]') + ' End of message.'
                })
            ),
            'sgnoreply@rit.edu',
            [recipients]
        )
        email.content_subtype = "html"
        res = email.send()
    return HttpResponse('%s'%res)

