from django.shortcuts import render, get_object_or_404, redirect
from django.core.exceptions import ObjectDoesNotExist
from django.views.generic import ListView, DetailView, View
from rest_framework.views import APIView
from .models import Item, OrderItem, Order, BillingAddress, Refund, Report, Category
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import CheckoutForm, RefundForm, ReportForm
from django.core.paginator import Paginator
from rest_framework import generics, viewsets
from .serializers import ItemSerializer
from rest_framework.response import Response
from rest_framework.decorators import action
import string
import random


def create_ref_code():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))


class SearchView(ListView):
    model = Item
    template_name = 'core/search.html'
    context_object_name = 'all_search_results'
    categories = Category.objects.all()
    extra_context = {
        'categories': categories
    }

    def get_queryset(self):
        result = super(SearchView, self).get_queryset()
        query = self.request.GET.get('search')
        if query:
            post_result = Item.objects.filter(title__contains=query)
            result = post_result
        else:
            result = None
        return result


def filter_by_category(request, slug):
    categories = Category.objects.all()
    category = Category.objects.get(slug=slug)
    items = Item.objects.filter(category=category)
    paginator = Paginator(items, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'items': items,
        'category': category,
        'categories': categories,
        'page_obj': page_obj,
    }
    return render(request, 'core/filter_by_category.html', context=context)


def remove_single_item_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(
                user=request.user,
                item=item,
                ordered=False)[0]
            if order_item.quantity > 1:
                order_item.quantity -= 1
                order_item.save()
            else:
                order.items.remove(order_item)
            messages.info(request, 'This item quantity was updated.')
            return redirect('core:order-summary')
        else:
            messages.info(request, 'This item was not in your cart.')
            return redirect('core:product', slug=slug)
    else:
        messages.info(request, 'You don\'t have an active order.')
        return redirect('core:product', slug=slug)


@login_required
def remove_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(
                user=request.user,
                item=item,
                ordered=False)[0]
            order.items.remove(order_item)
            messages.info(request, 'This item was removed from your cart.')
            return redirect('core:order-summary')
        else:
            messages.info(request, 'This item was not in your cart.')
            return redirect('core:order-summary')
    else:
        messages.info(request, 'You don\'t have an active order.')
        return redirect('core:order-summary')


@login_required
def add_to_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_item, created = OrderItem.objects.get_or_create(
        user=request.user,
        item=item,
        ordered=False)
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item.quantity += 1
            order_item.save()
            messages.info(request, 'Item quantity was updated.')
            return redirect('core:order-summary')
        else:
            messages.info(request, 'Item was added to your cart.')
            order.items.add(order_item)
            return redirect('core:product', slug=slug)
    else:
        ordered_date = timezone.now()
        order = Order.objects.create(user=request.user, ordered_date=ordered_date)
        order.items.add(order_item)
        messages.info(request, 'Item quantity was updated.')

    return redirect('core:product', slug=slug)


class CheckoutView(View):
    def get(self, *args, **kwargs):
        form = CheckoutForm()
        order = Order.objects.get(user=self.request.user, ordered=False)
        context = {
            'form': form,
            'order': order
        }
        return render(self.request, 'core/checkout.html', context)

    def post(self, *args, **kwargs):
        form = CheckoutForm(self.request.POST or None)
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            if form.is_valid():
                first_name = form.cleaned_data.get('first_name')
                last_name = form.cleaned_data.get('last_name')
                email = form.cleaned_data.get('email')
                phone_number = form.cleaned_data.get('phone_number')
                street_address = form.cleaned_data.get('street_address')
                country = form.cleaned_data.get('country')
                zip = form.cleaned_data.get('zip')
                # TODO: add functionality for these fields
                # same_shipping_address = form.cleaned_data.get('same_shipping_address')
                # save_info = form.cleaned_data.get('save_info')
                payment_option = form.cleaned_data.get('payment_option')
                billing_address = BillingAddress(
                    user=self.request.user,
                    first_name=first_name,
                    last_name=last_name,
                    email=email,
                    phone_number=phone_number,
                    street_address=street_address,
                    country=country,
                    zip=zip
                )
                billing_address.save()
                order.billing_address = billing_address

                order_items = order.items.all()
                order_items.update(ordered=True)
                for item in order_items:
                    item.save()

                order.ordered = True
                order.ref_code = create_ref_code()
                order.save()
                messages.success(self.request, 'Your order was successful!')
                return redirect('core:home')
            messages.warning(self.request, 'Failed checkout')
            return redirect('core:checkout')
        except ObjectDoesNotExist:
            messages.error(self.request, "You don't have an active order.")
            return redirect('core:order-summary')


class OrderSummaryView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            context = {
                "object": order,
            }
            return render(self.request, 'core/order_summary.html', context)
        except ObjectDoesNotExist:
            messages.error(self.request, "You don't have an active order.")
            return redirect('/')


class HomeView(ListView):
    model = Item
    template_name = 'core/home.html'
    context_object_name = 'items'
    categories = Category.objects.all()
    extra_context = {
        'categories': categories,
    }
    paginate_by = 12


class ItemDetailView(DetailView):
    model = Item
    template_name = 'core/product.html'


class RequestRefundView(View):
    def get(self, *args, **kwargs):
        form = RefundForm()
        context = {
            'form': form
        }
        return render(self.request, 'core/request_refund.html', context=context)

    def post(self, *args, **kwargs):
        form = RefundForm(self.request.POST)
        if form.is_valid():
            ref_code = form.cleaned_data.get('ref_code')
            message = form.cleaned_data.get('message')
            email = form.cleaned_data.get('email')
            try:
                order = Order.objects.get(ref_code=ref_code)
                order.refund_requested = True
                order.save()

                # store the refund
                refund = Refund()
                refund.order = order
                refund.reason = message
                refund.email = email
                refund.save()

                messages.success(self.request, 'Your request was received.')
                return redirect('core:request-refund')

            except ObjectDoesNotExist:
                messages.info(self.request, 'This order does not exist.')
                return redirect('core:request-refund')
        else:
            return render(self.request, 'core/request_refund.html')


def order_list(request):
    orders_list = Order.objects.filter(user=request.user).order_by('-start_date')
    if len(orders_list) < 1:
        messages.info(request, 'You have no orders.')
        return redirect('core:home')
    context = {
        'orders_list': orders_list,
    }
    return render(request, 'core/order_list.html', context=context)


def order_detail(request, pk):
    order = get_object_or_404(Order, pk=pk)
    order_items = order.items.all()
    context = {
        'order': order,
        'order_items': order_items,
    }
    return render(request, 'core/order_detail.html', context=context)


class ReportView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        pk = self.kwargs['pk']
        order = get_object_or_404(Order, pk=pk)
        form = ReportForm()
        form.fields['full_name'].widget.attrs[
            'value'] = order.billing_address.first_name + ' ' + order.billing_address.last_name
        form.fields['phone_number'].widget.attrs['value'] = order.billing_address.phone_number
        form.fields['email'].widget.attrs['value'] = order.billing_address.email
        form.fields['ref_code'].widget.attrs['value'] = order.ref_code
        context = {
            'form': form,
            'order': order,
        }
        return render(self.request, 'core/report.html', context=context)

    def post(self, *args, **kwargs):
        form = ReportForm(self.request.POST)
        if form.is_valid():
            reason = form.cleaned_data.get('message')
            full_name = form.cleaned_data.get('full_name')
            phone_number = form.cleaned_data.get('phone_number')
            email = form.cleaned_data.get('email')
            ref_code = form.cleaned_data.get('ref_code')

            try:
                order = Order.objects.get(ref_code=ref_code)

                report = Report()
                report.order = order
                report.reason = reason
                report.full_name = full_name
                report.phone_number = phone_number
                report.email = email
                report.ref_code = ref_code
                report.save()

                messages.info(self.request, 'Your report has been sent.')
                return redirect('core:order-list')
            except ObjectDoesNotExist:
                messages.info(self.request, 'This order does not exist.')
                return redirect('core:order-list')
        else:
            return render(self.request, 'core/report.html')


class PaymentView(View):
    def get(self, *args, **kwargs):
        return render(self.request, 'core/payment.html')
