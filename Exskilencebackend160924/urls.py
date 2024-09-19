"""Exskilencebackend160924 URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from Exskilence import views as ex,sqlviews as sql,pythonrun as ex_py,HTML_CSS_views as html_css,js_views as js , frontend_views as frontend
from Exskilence import coursecreatiton as pkgs
urlpatterns = [
    path('admin/', admin.site.urls),
    # Swapnodayaplacements
    path ('placement/', include('Exskilence.placements_urls')),
    path ('internshipreport/', include('Exskilence.urls')),

    # Exskilence
    path ('', ex.home),
    path ('fetch/', ex.fetch),

    path ('get/course/',ex.getcourse ),
    path ('getdays/',ex.getdays ),
    path ('days/qns/',ex.getQnslist ),
    path ('get/qn/data/',ex.getQn ),
    path ('submit/',ex.submit ),
    path ('nav/qn/',ex.nextQn ),
    path ('daycomplete/',ex.daycomplete ),
    # Sql
    path ('runsql/',sql.sql_query ),
    # Python
    path ('runpy/',ex_py.submit_python ),
    # Frontend
    
    path ('html/',html_css.html_page ),
    path ('css/',html_css.css_compare ),
    path ('js/',js.run_test_js ),
    path ('frontend/qns/',frontend.frontend_Questions_page ),
    path ('frontend/qns/data/',frontend.frontend_getQn ),
    path ('frontend/nav/qn/',frontend.frontend_nextQn ),

    path ('createpkgs/', pkgs.createpkgs),
    path ('coursepackages/', pkgs.coursepackages),
    path ('setusercourse/time', pkgs.assigncoursetime),
    path ('getcourselist/', pkgs.allCourses),
    path ('setusercourse/', pkgs.assigncourse),
    path ('studentlist/', pkgs.getallstudents),

    path ('filter/', pkgs.filteringStudents),

]
