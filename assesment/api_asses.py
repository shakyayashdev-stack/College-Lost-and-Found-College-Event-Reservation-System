from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from database_asses import get_session
from schemas_asses import Item, VALID_STATUSES



router = APIRouter()


def validate_item(item: Item):
    if not item.title.strip():
        raise HTTPException(
            status_code=422,
            detail="Title must not be empty"
        )

    if not item.description.strip() or len(item.description.strip()) < 5:
        raise HTTPException(
            status_code=422,
            detail="Description must contain meaningful text"
        )

    if item.status not in VALID_STATUSES:
        raise HTTPException(
            status_code=422,
            detail="Status must be Lost, Found, or Returned"
        )

    if not item.category.strip():
        raise HTTPException(
            status_code=422,
            detail="Category is required"
        )

    if not item.location.strip():
        raise HTTPException(
            status_code=422,
            detail="Location is required"
        )

    if not item.reported_by.strip():
        raise HTTPException(
            status_code=422,
            detail="Reported by is required"
        )



@router.post("/items", response_model=Item, status_code=201)
def create_item(
    item: Item,
    session: Session = Depends(get_session)
):
    validate_item(item)

    session.add(item)
    session.commit()
    session.refresh(item)

    return item



@router.get("/items", response_model=list[Item])
def get_items(
    session: Session = Depends(get_session)
):
    items = session.exec(select(Item)).all()
    return items


@router.get("/items/{item_id}", response_model=Item)
def get_item(
    item_id: int,
    session: Session = Depends(get_session)
):
    item = session.get(Item, item_id)

    if not item:
        raise HTTPException(
            status_code=404,
            detail="Item not found"
        )

    return item

@router.put("/items/{item_id}", response_model=Item)
def update_item(
    item_id: int,
    updated_item: Item,
    session: Session = Depends(get_session)
):
    validate_item(updated_item)

    item = session.get(Item, item_id)

    if not item:
        raise HTTPException(
            status_code=404,
            detail="Item not found"
        )

    item.title = updated_item.title
    item.description = updated_item.description
    item.category = updated_item.category
    item.location = updated_item.location
    item.reported_by = updated_item.reported_by
    item.status = updated_item.status

    session.add(item)
    session.commit()
    session.refresh(item)

    return item

@router.delete("/items/{item_id}")
def delete_item(
    item_id: int,
    session: Session = Depends(get_session)
):
    item = session.get(Item, item_id)

    if not item:
        raise HTTPException(
            status_code=404,
            detail="Item not found"
        )

    session.delete(item)
    session.commit()

    return {
        "message": "Item deleted successfully",
        "item_id": item_id
    }

@router.get("/items/status/{status}", response_model=list[Item])
def get_items_by_status(
    status: str,
    session: Session = Depends(get_session)
):
    if status not in VALID_STATUSES:
        raise HTTPException(
            status_code=422,
            detail="Status must be Lost, Found, or Returned"
        )

    statement = select(Item).where(Item.status == status)
    items = session.exec(statement).all()

    return items

@router.get("/items/category/{category}", response_model=list[Item])
def get_items_by_category(
    category: str,
    session: Session = Depends(get_session)
):
    statement = select(Item).where(Item.category == category)
    items = session.exec(statement).all()

    return items