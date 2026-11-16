from src.models import (
    Apartment,
    ApartmentSettlement,
    Bill,
    Parameters,
    Tenant,
    TenantSettlement,
    Transfer,
)


class Manager:
    def __init__(self, parameters: Parameters):
        self.parameters = parameters 

        self.apartments = {}
        self.tenants = {}
        self.transfers = []
        self.bills = []
       
        self.load_data()

    def load_data(self):
        self.apartments = Apartment.from_json_file(self.parameters.apartments_json_path)
        self.tenants = Tenant.from_json_file(self.parameters.tenants_json_path)
        self.transfers = Transfer.from_json_file(self.parameters.transfers_json_path)
        self.bills = Bill.from_json_file(self.parameters.bills_json_path)

    def check_tenants_apartment_keys(self) -> bool:
        for tenant in self.tenants.values():
            if tenant.apartment not in self.apartments:
                return False
        return True

    def get_apartment_costs(self, apartment_key, year=None, month=None):
        if apartment_key not in self.apartments:
            return None
        if month is not None and not 1 <= month <= 12:
            raise ValueError("month must be between 1 and 12")
        if month is not None and year is None:
            raise ValueError("year is required when month is provided")

        return sum(
            bill.amount_pln
            for bill in self.bills
            if bill.apartment == apartment_key
            and (year is None or bill.settlement_year == year)
            and (month is None or bill.settlement_month == month)
        )

    def create_apartment_settlement(self, apartment_key, year, month):
        total_bills = self.get_apartment_costs(apartment_key, year, month)
        if total_bills is None:
            return None

        return ApartmentSettlement(
            apartment=apartment_key,
            month=month,
            year=year,
            total_rent_pln=0.0,
            total_bills_pln=total_bills,
            total_due_pln=-total_bills,
        )

    def create_tenant_settlements(self, apartment_key, year, month):
        apartment_settlement = self.create_apartment_settlement(
            apartment_key, year, month
        )
        if apartment_settlement is None:
            return []

        tenants = [
            tenant
            for tenant in self.tenants.values()
            if tenant.apartment == apartment_key
        ]
        if not tenants:
            return []

        bills_per_tenant = (
            apartment_settlement.total_bills_pln / len(tenants)
        )
        return [
            TenantSettlement(
                tenant=tenant.name,
                apartment_settlement=apartment_key,
                month=month,
                year=year,
                rent_pln=0.0,
                bills_pln=bills_per_tenant,
                total_due_pln=bills_per_tenant,
                balance_pln=-bills_per_tenant,
            )
            for tenant in tenants
        ]