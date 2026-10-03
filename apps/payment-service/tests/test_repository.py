from sqlalchemy.ext.asyncio import AsyncSession

from domain.model.payment import Payment, Status
from repository.payment import PaymentRepository


async def test_add(db_session: AsyncSession) -> None:
    repo = PaymentRepository(db_session)

    payment = Payment(
        group_id=1,
        user_id="test123user",
        amount=100,
        currency="USD",
        status=Status.COMPLETED,
        stripe_session_id="100"
    )

    result = await repo.add(payment)

    assert result.status == Status.COMPLETED
    assert result.group_id == 1

async def test_add_all(db_session: AsyncSession) -> None:
    repo = PaymentRepository(db_session)

    payment = Payment(
        group_id=1,
        user_id="test123user",
        amount=100,
        currency="USD",
        status=Status.COMPLETED,
        stripe_session_id="100"
    )
    payment_2 = Payment(
        group_id=2,
        user_id="test123user",
        amount=50,
        currency="USD",
        status=Status.COMPLETED,
        stripe_session_id="100"
    )

    result = await repo.add_all([payment, payment_2])

    assert result[0].amount == 100
    assert result[1].amount == 50

async def test_get_by_id(db_session: AsyncSession) -> None:
    repo = PaymentRepository(db_session)

    payment = Payment(
        group_id=1,
        user_id="test123user",
        amount=100,
        currency="USD",
        status=Status.COMPLETED,
        stripe_session_id="100"
    )

    _ = await repo.add(payment)

    result = await repo.get_by_id(payment.id)
    assert result is not None
    assert result.status == Status.COMPLETED
    assert result.group_id == 1

async def test_get_by_stripe_session_id(db_session: AsyncSession) -> None:
    repo = PaymentRepository(db_session)

    payment = Payment(
        group_id=1,
        user_id="test123user",
        amount=100,
        currency="USD",
        status=Status.COMPLETED,
        stripe_session_id="100"
    )

    _ = await repo.add(payment)

    result = await repo.get_by_stripe_session_id("100")

    assert result is not None
    assert result.currency == "USD"
    assert result.group_id == 1

async def test_get_by_active_reservation_id(db_session: AsyncSession) -> None:
    repo = PaymentRepository(db_session)

    payment = Payment(
        group_id=1,
        user_id="test123user",
        amount=100,
        currency="USD",
        status=Status.COMPLETED,
        stripe_session_id="100"
    )

    _ = await repo.add(payment)

    result = await repo.get_by_active_group_id(payment.group_id)

    assert result is not None
    assert result.currency == "USD"
    assert result.status == Status.COMPLETED



async def test_get_all(db_session: AsyncSession) -> None:
    repo = PaymentRepository(db_session)

    payment = Payment(
        group_id=1,
        user_id="test123user",
        amount=100,
        currency="USD",
        status=Status.COMPLETED,
        stripe_session_id="100"
    )
    payment_2 = Payment(
        group_id=2,
        user_id="test123user",
        amount=50,
        currency="USD",
        status=Status.COMPLETED,
        stripe_session_id="100"
    )

    _ = await repo.add_all([payment, payment_2])

    result = await repo.get_all()

    assert result[0].amount == 100
    assert result[1].amount == 50

async def test_update(db_session: AsyncSession) -> None:
    repo = PaymentRepository(db_session)

    payment = Payment(
        group_id=1,
        user_id="test123user",
        amount=100,
        currency="USD",
        status=Status.COMPLETED,
        stripe_session_id="100"
    )
    payment_update = Payment(
        group_id=1,
        user_id="test123user",
        amount=50,
        currency="USD",
        status=Status.COMPLETED,
        stripe_session_id="100"
    )

    _ = await repo.add(payment)

    result = await repo.update(payment_update)

    assert result.amount == 50

async def test_delete_by_id(db_session: AsyncSession) -> None:
    repo = PaymentRepository(db_session)

    payment = Payment(
        group_id=1,
        user_id="test123user",
        amount=100,
        currency="USD",
        status=Status.COMPLETED,
        stripe_session_id="100"
    )
    _ = await repo.add(payment)
    await repo.delete_by_id(payment.id)

    result = await repo.get_by_id(payment.id)

    assert result is None






