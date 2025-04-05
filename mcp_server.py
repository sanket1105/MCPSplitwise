from typing import Dict, List

import requests
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

# Load the Splitwise access token
try:
    with open("splitwise_access_token.txt", "r") as f:
        access_token = f.read().strip()
except FileNotFoundError:
    raise FileNotFoundError(
        "splitwise_access_token.txt not found. Run get_access_token.py first."
    )


# Define data models
class BillItem(BaseModel):
    item: str
    price: float


class SplitwiseGroup(BaseModel):
    group_name: str
    expense_date: str
    split_equally: bool
    each_share: float


class BillData(BaseModel):
    items: List[BillItem]
    total: float
    splitwise_group: SplitwiseGroup


@app.post("/process_bill")
async def process_bill(data: BillData):
    try:
        # Extract data
        group_name = data.splitwise_group.group_name
        total = data.total
        expense_date = data.splitwise_group.expense_date
        split_equally = data.splitwise_group.split_equally
        each_share = data.splitwise_group.each_share

        # Fetch the group_id by group_name
        group_id = get_group_id_by_name(group_name, access_token)
        if not group_id:
            raise ValueError(f"Group '{group_name}' not found")

        # Get group members to validate the split
        members = get_group_members(group_id, access_token)
        num_members = len(members)
        if num_members == 0:
            raise ValueError("No members found in the group")

        # Validate the split
        calculated_total = each_share * num_members
        if abs(calculated_total - total) > 0.01:
            raise ValueError(
                f"Split validation failed: {each_share} * {num_members} = {calculated_total}, but total is {total}"
            )

        # Create the expense in Splitwise
        splitwise_url = "https://secure.splitwise.com/api/v3.0/create_expense"
        headers = {"Authorization": f"Bearer {access_token}"}

        # Prepare the expense description
        items_list = ", ".join([item.item for item in data.items])
        description = f"Bill split: {items_list}"

        # Create the payload
        payload = {
            "cost": str(total),
            "description": description,
            "date": expense_date,
            "group_id": group_id,
            "split_equally": split_equally,
        }

        # If not splitting equally, you’d add user shares here (for future enhancement)
        if not split_equally:
            raise NotImplementedError("Unequal splitting not implemented yet")

        # Send the request to Splitwise
        response = requests.post(splitwise_url, headers=headers, data=payload)
        response.raise_for_status()

        return {"status": "success", "message": "Expense added to Splitwise"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


def get_group_id_by_name(group_name: str, token: str) -> int:
    """Fetch the group_id for a group by its name."""
    url = "https://secure.splitwise.com/api/v3.0/get_groups"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    groups = response.json()["groups"]
    for group in groups:
        if group["name"].lower() == group_name.lower():
            return group["id"]
    return None


def get_group_members(group_id: int, token: str) -> List[Dict]:
    """Fetch the members of a group by its group_id."""
    url = f"https://secure.splitwise.com/api/v3.0/get_group/{group_id}"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    group_data = response.json()
    return group_data["group"]["members"]
