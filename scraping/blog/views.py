from django.shortcuts import render
# from django.http import HttpResponse
from bs4 import BeautifulSoup
from django import forms
import requests
import re
import pandas as pd

# link = 'http://www.ffbb.com/jouer/trouver-un-club?DepartementClub=45'
# page_r = requests.get(link, timeout=5)
# page_c = BeautifulSoup(page_r.content, "html.parser")
textContent = []


def email_in_page(page_container):
    page = page_container.find('body').text
    pattern = re.compile(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+')
    emails = pattern.findall(page)
    write_excel(emails, "Email")
    return emails


def phone_number(page_container):
    page = page_container.find('body').text
    pattern = re.compile(r'(?:(?:\+|00)33|0)\s*[1-9](?:[\s.-]*\d{2}){4}')
    phones = pattern.findall(page)
    write_excel(phones, "Number")
    return phones


def location(page_container):
    page = page_container.find('body').text
    pattern = re.compile(r'\s\d{1,3},? [a-zA-Z]+ (?:\D+\s)+')
    cities = pattern.findall(page)
    write_excel(cities, "city")
    return cities


def zip_code(page_container):
    page = page_container.find('body').text
    pattern = re.compile(r'\s[0-9]{5,5}\s')
    zips = pattern.findall(page)
    write_excel(zips, "zip")
    return zips


def web_site(page_container):
    page = page_container.find('body').text
    pattern = re.compile(
        r'(https?:\/\/(?:www\.|(?!www))[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|www\.[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|https?:\/\/(?:www\.|(?!www))[a-zA-Z0-9]\.[^\s]{2,}|www\.[a-zA-Z0-9]\.[^\s]{2,})')
    webs = pattern.findall(page)
    write_excel(webs, "links")
    return webs


def write_excel(data, column):
    l = []
    for tr in data:
        l.append(tr)
    df = pd.DataFrame(l, columns=[column])
    writer = pd.ExcelWriter('simple.xlsx', engine='xlsxwriter')
    df.to_excel(writer, sheet_name='Sheet1')
    writer.save()


def pages_loop(page):
    email_in_page(page)
    phone_number(page)
    location(page)
    zip_code(page)
    web_site(page)


# pages_loop(page_c)


class HomeForm(forms.Form):
    site = forms.URLField()


def home(request):
    if request.method == 'POST':
        form = HomeForm(request.POST)
        if form.is_valid():
            site = form.cleaned_data['site']
            print(site)
            page_r = requests.get(site, timeout=5)
            page_c = BeautifulSoup(page_r.content, "html.parser")
            content = {
                'site': site,
                'email': email_in_page(page_c),
                'phone': phone_number(page_c),
                'location': location(page_c),
                'zip': zip_code(page_c),
                'web': web_site(page_c)
            }
            print(content)
            return render(request, 'blog/about.html', {'infos': content})

    form = HomeForm()
    return render(request, 'blog/home.html', {'form': form})


def about(request):
    return render(request, 'blog/about.html')
