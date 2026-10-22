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


def customer_list(request):
    customers = Customer.objects.filter(
        delete_flag=0
    ).order_by('customer_code')

    return render(request, 'psys/customer_list.html', {
        'customers': customers
    })


from django.db.models import Count, Sum
from django.db.models.functions import TruncMonth
from .models import Orders


def monthly_order_summary(request):
    summaries = (
        Orders.objects
        .filter(order_date__isnull=False)
        .annotate(month=TruncMonth('order_date'))
        .values('month')
        .annotate(
            order_count=Count('order_no'),
            total_sales=Sum('total_price', default=0)
        )
        .order_by('month')
    )

    return render(request, 'psys/monthly_order_summary.html', {
        'summaries': summaries
    })


from django.db.models.functions import TruncYear


def yearly_order_summary(request):
    summaries = (
        Orders.objects
        .filter(order_date__isnull=False)
        .annotate(year=TruncYear('order_date'))
        .values('year')
        .annotate(
            order_count=Count('order_no'),
            total_sales=Sum('total_price', default=0)
        )
        .order_by('year')
    )

    return render(request, 'psys/yearly_order_summary.html', {
        'summaries': summaries
    })


from .models import OrderDetails


def product_order_summary(request):
    summaries = (
        OrderDetails.objects
        .values('item_code', 'item_code__item_name')
        .annotate(
            order_count=Count('order_no', distinct=True),
            total_quantity=Sum('order_num', default=0),
            total_sales=Sum('order_price', default=0)
        )
        .order_by('item_code')
    )

    return render(request, 'psys/product_order_summary.html', {
        'summaries': summaries
    })