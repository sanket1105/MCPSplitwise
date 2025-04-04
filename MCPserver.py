from typing import List

import requests
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

# Load the Splitwise access token
with open("splitwise_access_token.txt", "r") as f:
    access_token = f.read().strip()


# Define data models
class BillItem(BaseModel):
    person: str
    item: str
    cost: float


class BillData(BaseModel):
    items: List[BillItem]
    splitwise_group_id: int


@app.post("/process_bill")
async def process_bill(data: BillData):
    try:
        # Group expenses by person
        expense_data = {}
        for item in data.items:
            if item.person not in expense_data:
                expense_data[item.person] = {"items": [], "total": 0.0}
            expense_data[item.person]["items"].append(item.item)
            expense_data[item.person]["total"] += item.cost

        # Send to Splitwise
        splitwise_url = "https://secure.splitwise.com/api/v3.0/create_expense"
        headers = {"Authorization": f"Bearer {access_token}"}

        for person, details in expense_data.items():
            payload = {
                "cost": str(details["total"]),
                "description": f"Bill split: {', '.join(details['items'])}",
                "group_id": data.splitwise_group_id,
                "split_equally": False,
                "users__0__user_id": get_splitwise_user_id(
                    person, access_token, data.splitwise_group_id
                ),
                "users__0__paid_share": "0.00",
                "users__0__owed_share": str(details["total"]),
            }
            response = requests.post(splitwise_url, headers=headers, data=payload)
            response.raise_for_status()

        return {"status": "success", "message": "Expenses added to Splitwise"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


def get_splitwise_user_id(name: str, token: str, group_id: int) -> int:
    url = f"https://secure.splitwise.com/api/v3.0/get_group/{group_id}"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(url, headers=headers)
    users = {
        user["user"]["first_name"]: user["user"]["id"]
        for user in response.json()["group"]["members"]
    }
    return users.get(name, 0)  # Handle missing users gracefully
