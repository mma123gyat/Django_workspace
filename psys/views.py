from django.shortcuts import render
from .models import Customer


def customer_search(request):
    customer = None
    error_message = None

    customer_code = request.GET.get('customer_code')

    if customer_code:
        try:
            customer = Customer.objects.get(
                customer_code=customer_code,
                delete_flag=0
            )
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
    year = request.GET.get('year', '').strip()
    month = request.GET.get('month', '').strip()

    summaries = []
    grand_total = 0
    error_message = None

    if year or month:
        if not (
            year.isdigit()
            and month.isdigit()
            and 1900 <= int(year) <= 2100
            and 1 <= int(month) <= 12
        ):
            error_message = '正しい年と月を入力してください。'
        else:
            orders = Orders.objects.filter(
                order_date__year=int(year),
                order_date__month=int(month)
            )

            summaries = orders.values(
                'customer_code',
                'customer_code__customer_name'
            ).annotate(
                total_sales=Sum('total_price', default=0)
            ).order_by('customer_code')

            grand_total = orders.aggregate(
                total=Sum('total_price', default=0)
            )['total']

    return render(request, 'psys/monthly_order_summary.html', {
        'year': year,
        'month': month,
        'summaries': summaries,
        'grand_total': grand_total,
        'error_message': error_message,
    })


from django.db.models.functions import TruncYear


def yearly_order_summary(request):
    year = request.GET.get('year', '').strip()

    summaries = []
    grand_total = 0
    error_message = None

    if year:
        if not year.isdigit() or not (1900 <= int(year) <= 2100):
            error_message = '正しい年を入力してください。'
        else:
            orders = Orders.objects.filter(
                order_date__year=int(year)
            )

            summaries = orders.values(
                'customer_code',
                'customer_code__customer_name'
            ).annotate(
                total_sales=Sum('total_price', default=0)
            ).order_by('customer_code')

            grand_total = orders.aggregate(
                total=Sum('total_price', default=0)
            )['total']

    return render(request, 'psys/yearly_order_summary.html', {
        'year': year,
        'summaries': summaries,
        'grand_total': grand_total,
        'error_message': error_message,
    })


from .models import OrderDetails


def product_order_summary(request):
    customer_code = request.GET.get('customer_code', '').strip()

    customer = None
    summaries = []
    grand_total = 0
    error_message = None

    if customer_code:
        customer = Customer.objects.filter(
            customer_code=customer_code
        ).first()

        if customer is None:
            error_message = '該当する得意先が見つかりません。'
        else:
            details = OrderDetails.objects.filter(
                order_no__customer_code=customer
            )

            summaries = (
                details
                .values(
                    'item_code',
                    'item_code__item_name',
                    'item_code__price'
                )
                .annotate(
                    total_quantity=Sum('order_num', default=0),
                    total_sales=Sum('order_price', default=0)
                )
                .order_by('item_code')
            )

            grand_total = details.aggregate(
                total=Sum('order_price', default=0)
            )['total']

    return render(request, 'psys/product_order_summary.html', {
        'customer_code': customer_code,
        'customer': customer,
        'summaries': summaries,
        'grand_total': grand_total,
        'error_message': error_message,
    })



from functools import wraps
from hmac import compare_digest

from django.shortcuts import redirect
from django.views.decorators.http import require_POST
from .models import Employee


def employee_login(request):
    if request.session.get('employee_no'):
        return redirect('customer_list')

    error_message = None

    if request.method == 'POST':
        employee_no = request.POST.get('employee_no', '').strip()
        password = request.POST.get('password', '')

        employee = Employee.objects.filter(
            employee_no=employee_no
        ).first()

        if (
            employee is not None
            and password
            and compare_digest(
                (employee.password or '').encode('utf-8'),
                password.encode('utf-8')
            )
        ):
            request.session.cycle_key()
            request.session['employee_no'] = employee.employee_no
            request.session['employee_name'] = employee.employee_name

            return redirect('customer_list')

        error_message = '従業員番号またはパスワードが違います。'

    return render(request, 'psys/login.html', {
        'error_message': error_message,
    })


@require_POST
def employee_logout(request):
    request.session.flush()
    return redirect('employee_login')


def employee_login_required(view_func):
    @wraps(view_func)
    def wrapped(request, *args, **kwargs):
        if not request.session.get('employee_no'):
            return redirect('employee_login')
        return view_func(request, *args, **kwargs)

    return wrapped