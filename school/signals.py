from django.db.models.signals import pre_save,post_delete
from django.dispatch import receiver
from .models import Session, EnrolledPackage  
from datetime import timedelta
from django.core.exceptions import ObjectDoesNotExist


@receiver(post_delete, sender=Session)
def update_enrolled_package_hours(sender, instance, **kwargs):
  
    
    enrolled_package = instance.enrolled_package

    try:
        package_type = enrolled_package.package_type

        time_sesion = timedelta(days=0, hours=0, minutes=0, seconds=0)
    
    
        for session in enrolled_package.sessions.all():
            if session.session_duration is not None:
                time_sesion += session.session_duration

        enrolled_package.consumed_time = time_sesion
        m, s = divmod(time_sesion.total_seconds(), 60)
        h, m = divmod(m, 60)
        enrolled_package.consumed_hours = '{:d}:{:02d}:{:02d} Hrs'.format(int(h), int(m), int(s))

        limite = package_type.hours
        limite_timedelta = timedelta(days=0, hours=limite, minutes=0, seconds=0)
        remaining_time = limite_timedelta - time_sesion

        time_0 = timedelta(days=0, hours=0, minutes=0, seconds=0)
        if remaining_time >= time_0:
            enrolled_package.remaining_time = remaining_time
            m, s = divmod(remaining_time.total_seconds(), 60)
            h, m = divmod(m, 60)
            enrolled_package.remaining_hours = '{:d}:{:02d}:{:02d} Hrs'.format(int(h), int(m), int(s))
        else:
            enrolled_package.remaining_time = time_0
            m, s = divmod(time_0.total_seconds(), 60)
            h, m = divmod(m, 60)
            enrolled_package.remaining_hours = '{:d}:{:02d}:{:02d} Hrs'.format(int(h), int(m), int(s))

        if time_sesion >= timedelta(days=0, hours=limite, minutes=0, seconds=0):
            enrolled_package.status = False
        else:
            enrolled_package.status = True

        enrolled_package.save(edit_from_session=True)
    
    except ObjectDoesNotExist:
            pass  


@receiver(pre_save, sender=Session)
def calculate_session_duration_and_update_package(sender, instance, **kwargs):
        if instance.start_time and instance.end_time:
            instance.session_duration = instance.end_time - instance.start_time
        else:
            instance.session_duration = None
        #Obtener la instancia de EnrolledPackage asociada a la sesión
        enrolled_package = instance.enrolled_package  
        # Calcular el tiempo consumido para el EnrolledPackage
        time_sesion = timedelta(days=0, hours=0, minutes=0, seconds=0)

        for session in enrolled_package.sessions.exclude(id=instance.id):
            if session.session_duration is not None:
                time_sesion += session.session_duration   

        # Agregar el tiempo de la sesión actual al cálculo
        if instance.session_duration is not None:
            time_sesion += instance.session_duration
       
        enrolled_package.consumed_time = time_sesion
        m, s = divmod(time_sesion.total_seconds(), 60)
        h, m = divmod(m, 60)
        enrolled_package.consumed_hours = '{:d}:{:02d}:{:02d} Hrs'.format(int(h),int(m),int(s))    
        
        limite = enrolled_package.package_type.hours
        limite_timedelta =  timedelta(days=0,hours=limite,minutes=0,seconds=0)
        remaining_time = limite_timedelta - time_sesion
        
        time_0 = timedelta(days=0,hours=0,minutes=0,seconds=0)
        if remaining_time >= time_0:
            enrolled_package.remaining_time = remaining_time
            m, s = divmod(remaining_time.total_seconds(), 60)
            h, m = divmod(m, 60)
            enrolled_package.remaining_hours  = '{:d}:{:02d}:{:02d} Hrs'.format(int(h),int(m),int(s))
        
        else:
            enrolled_package.remaining_time = time_0
            m, s = divmod(time_0.total_seconds(), 60)
            h, m = divmod(m, 60)
            enrolled_package.remaining_hours = '{:d}:{:02d}:{:02d} Hrs'.format(int(h),int(m),int(s))    
        
        if time_sesion >= timedelta(days=0,hours=limite,minutes=0,seconds=0):
            enrolled_package.status = False 
        else:
            enrolled_package.status = True
        enrolled_package.save(edit_from_session=True)    
