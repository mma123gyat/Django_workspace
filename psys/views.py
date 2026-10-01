from django.shortcuts import render
from .models import Customer


def customer_search(request):
    customer = None
    error_message = None

    customer_code = request.GET.get('customer_code')

    if customer_code:
        try:
            customer = Customer.objects.get(customer_code=customer_code)
        except Customer.DoesNotExist:
            error_message = '該当する得意先が見つかりません。'

    return render(request, 'psys/customer_search.html', {
        'customer': customer,
        'error_message': error_message,
    })

from django.db import transaction
from django.shortcuts import render
from .models import Customer, CustomerNumbering


def customer_register(request):
    message = None
    error_message = None

    if request.method == 'POST':
        customer_name = request.POST.get('customer_name')
        customer_telno = request.POST.get('customer_telno')
        customer_postalcode = request.POST.get('customer_postalcode')
        customer_address = request.POST.get('customer_address')
        discount_rate = request.POST.get('discount_rate')

        try:
            with transaction.atomic():
                numbering = CustomerNumbering.objects.select_for_update().first()

                if numbering is None:
                    error_message = '得意先採番情報がありません。'
                else:
                    next_number = numbering.customer_code + 1
                    customer_code = f'RA{next_number:04d}'

                    Customer.objects.create(
                        customer_code=customer_code,
                        customer_name=customer_name,
                        customer_telno=customer_telno,
                        customer_postalcode=customer_postalcode,
                        customer_address=customer_address,
                        discount_rate=int(discount_rate) if discount_rate else 0,
                        delete_flag=0,
                    )

                    CustomerNumbering.objects.filter(
                        customer_code=numbering.customer_code
                    ).update(
                        customer_code=next_number
                    )

                    message = f'{customer_code} を登録しました。'

        except Exception as e:
            error_message = f'登録に失敗しました：{e}'

    return render(request, 'psys/customer_register.html', {
        'message': message,
        'error_message': error_message,
    })


def customer_delete(request):
    customer = None
    message = None
    error_message = None

    if request.method == 'POST':
        customer_code = request.POST.get('customer_code','').strip()

        updated = Customer.objects.filter(
            customer_code=customer_code,
            delete_flag=0
        ).update(delete_flag=1)

        if updated:
            message =f'{customer_code}を削除しました。'
        else:
            error_message ='削除対象の得意先が見つかりません。'
    else:
        customer_code = request.GET.get('customer_code','').strip()

        if customer_code:
            customer = Customer.objects.filter(
                customer_code=customer_code,
                delete_flag=0
            ).first()

            if customer is None:
                error_message = '該当する得意先が見つかりません。'
    return render(request,'psys/customer_delete.html',{
        'customer':customer,
        'message':message,
        'error_message':error_message
    })

from .forms import CustomerEditForm


def customer_edit(request):
    customer = None
    form = None
    message = None
    error_message = None

    if request.method == 'POST':
        customer_code = request.POST.get('customer_code', '').strip()
    else:
        customer_code = request.GET.get('customer_code', '').strip()

    if customer_code:
        customer = Customer.objects.filter(
            customer_code=customer_code,
            delete_flag=0
        ).first()

        if customer is None:
            error_message = '該当する得意先が見つかりません。'

        elif request.method == 'POST':
            form = CustomerEditForm(request.POST, instance=customer)

            if form.is_valid():
                form.save()
                message = f'{customer_code} の情報を変更しました。'
                form = CustomerEditForm(instance=customer)

        else:
            form = CustomerEditForm(instance=customer)

    return render(request, 'psys/customer_edit.html', {
        'customer': customer,
        'form': form,
        'message': message,
        'error_message': error_message,
        'customer_code': customer_code,
    })