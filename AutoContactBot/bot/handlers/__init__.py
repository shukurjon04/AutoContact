from aiogram import Dispatcher
from .start import router as start_router
from .subscription import router as subscription_router
from .profile import router as profile_router
from .payment import router as payment_router
from .receipt import router as receipt_router
from .errors import router as errors_router


def register_all_routers(dp: Dispatcher) -> None:
    dp.include_router(start_router)
    dp.include_router(subscription_router)
    dp.include_router(payment_router)
    dp.include_router(receipt_router)
    dp.include_router(profile_router)
    # Error handler must be last
    dp.include_router(errors_router)
