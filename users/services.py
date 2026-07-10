import stripe
from django.conf import settings

# Инициализация секретным ключом
stripe.api_key = settings.STRIPE_API_KEY


def create_stripe_product(name: str) -> str:
    """ Создает продукт в Stripe и возвращает его ID. """
    product = stripe.Product.create(name=name)
    return product.id


def create_stripe_price(amount: int, product_id: str) -> str:
    """ Создает цену в Stripe для конкретного продукта и возвращает ее ID. """

    price = stripe.Price.create(
        currency="rub",  # или "usd", в зависимости от требований проекта
        unit_amount=int(amount * 100),  # Переводим рубли в копейки
        product=product_id,
    )
    return price.id


def create_stripe_session(price_id: str) -> tuple[str, str]:
    """ Создает платежную сессию в Stripe и возвращает данные для оплаты. """

    session = stripe.checkout.Session.create(
        success_url="http://127.0.0.8000",  # Страница успешной оплаты
        line_items=[{"price": price_id, "quantity": 1}],
        mode="payment",
    )
    return session.url, session.id


def retrieve_stripe_session_status(session_id: str) -> str:
    """ Получает данные сессии из Stripe и возвращает статус оплаты (payment_status). """

    session = stripe.checkout.Session.retrieve(session_id)
    return session.payment_status  # Вернет 'unpaid', 'paid' или 'no_payment_required'

