import mesa
import numpy as np
import pandas as pd
import random
from agents import GovernmentAgent
from agents import FirmAgent
from agents import HouseholdAgent

class EconomicSimulationModel(mesa.Model):
    def __init__(self):
        super().__init__()

        self.datacollector = mesa.DataCollector(
            model_reporters={
                "Reserves": lambda m: m.government_agent.reserves,
                "Yearly Public Spending": lambda m: m.government_agent.yearly_public_spending,
            },
            agent_reporters= {
                 # Firm agent fields
                "FirmType": lambda a: getattr(a, "firm_type", None),
                "Profit": lambda a: getattr(a, "profit", None),
                "Inventory": lambda a: getattr(a, "inventory", None),
                "ProductPrice": lambda a: getattr(a, "product_price", None),
                "RevenuePerEmployee": lambda a: getattr(a, "revenue_per_employee", None),
                "ProductionLevel": lambda a: getattr(a, "production_level", None),
                "NumEmployees": lambda a: getattr(a, "num_employees", None),
                "DemandReceived": lambda a: getattr(a, "demand_received", None),
                "InventoryDemandRatio": lambda a: getattr(a, "inventory_demand_ratio", None),
                "SellThroughRate": lambda a: getattr(a, "sell_through_rate", None),
                "ProductionCapacity": lambda a: getattr(a, "production_capacity", None),
                "Revenue": lambda a: getattr(a, "revenue", None),
                "Costs": lambda a: getattr(a, "costs", None),
                "ProfitMargin": lambda a: getattr(a, "profit_margin", None),
                "ProducedUnits": lambda a: getattr(a, "produced_units", None),
                

                # Household agent fields
                "IncomeBracket": lambda a: getattr(a, "income_bracket", None),
                "NumPeople": lambda a: getattr(a, "num_people", None),
                "SpendRatio": lambda a: getattr(a, "spend_ratio", None),
                "PostTaxIncome": lambda a: getattr(a, "total_income_posttax", None),
                "HouseholdExpense": lambda a: getattr(a, "total_household_expense", None),
                "HouseholdSavings": lambda a: getattr(a, "total_household_savings", None),
                "HealthLevel": lambda a: getattr(a, "health_level", None),
                "Welfare": lambda a: getattr(a, "welfare", None),
                
                # Person agent fields
                "SkillLevel": lambda a: getattr(a, "skill_level", None),
                "SkillType": lambda a: getattr(a, "skill_type", None),
                "JobLevel": lambda a: getattr(a, "job_level", None),
                "IsEmployed": lambda a: 1 if getattr(a, "employer", None) is not None else 0,
                "Wage": lambda a: getattr(a, "wage", None)
            }
        )
        
        self.government_agent = GovernmentAgent.create_agents(model=self, n=1)[0]
        
        # Create firms with different areas and suitable parameters
        
        # --- NECESSITY FIRMS ---
        
        # Physical firms (manufacturing, construction, farming) - 35 firms
        n_physical = 25
        FirmAgent.create_agents(
            model=self,
            n=n_physical,
            firm_type="necessity",
            firm_area="physical",
            product=[f"Physical_{i}" for i in range(n_physical)],
            production_capacity=[random.randint(4000, 9000) for _ in range(n_physical)],
            profit_margin=0.12,
            production_cost=[random.uniform(1.8, 4.5) for _ in range(n_physical)],
            entry_wage=[random.randint(20000, 25000) for _ in range(n_physical)],
            num_employees=[random.randint(30, 120) for _ in range(n_physical)],
            production_level=[random.uniform(0.7, 1) for _ in range(n_physical)]
        )
        
        # Service firms (retail, food service, basic services) - 40 firms
        n_service = 30
        FirmAgent.create_agents(
            model=self,
            n=n_service,
            firm_type="necessity",
            firm_area="service",
            product=[f"Service_{i}" for i in range(n_service)],
            production_capacity=[random.randint(3000, 7000) for _ in range(n_service)],
            profit_margin=0.09,
            production_cost=[random.uniform(1.5, 3.5) for _ in range(n_service)],
            entry_wage=[random.randint(18000, 22000) for _ in range(n_service)],
            num_employees=[random.randint(15, 50) for _ in range(n_service)],
            production_level=[random.uniform(0.6, 0.9) for _ in range(n_service)]
        )
        
        # --- LUXURY FIRMS ---
        
        # Technical firms (tech companies, engineering) - 20 firms
        n_technical = 10
        FirmAgent.create_agents(
            model=self,
            n=n_technical,
            firm_type="luxury",
            firm_area="technical",
            product=[f"Technical_{i}" for i in range(n_technical)],
            production_capacity=[random.randint(300, 700) for _ in range(n_technical)],
            profit_margin=0.35,
            production_cost=[random.uniform(50.0, 200.0) for _ in range(n_technical)],
            entry_wage=[random.randint(60000, 75000) for _ in range(n_technical)],
            num_employees=[random.randint(10, 80) for _ in range(n_technical)],
            production_level=[random.uniform(0.5, 0.9) for _ in range(n_technical)]
        )
        
        # Creative firms (design, arts, media) - 15 firms
        n_creative = 5
        FirmAgent.create_agents(
            model=self,
            n=n_creative,
            firm_type="luxury",
            firm_area="creative",
            product=[f"Creative_{i}" for i in range(n_creative)],
            production_capacity=[random.randint(200, 500) for _ in range(n_creative)],
            profit_margin=0.45,
            production_cost=[random.uniform(40.0, 100.0) for _ in range(n_creative)],
            entry_wage=[random.randint(45000, 60000) for _ in range(n_creative)],
            num_employees=[random.randint(5, 30) for _ in range(n_creative)],
            production_level=[random.uniform(0.4, 0.8) for _ in range(n_creative)]
        )
        
        # Social firms (management consulting, education) - 10 firms
        n_social = 5
        FirmAgent.create_agents(
            model=self,
            n=n_social,
            firm_type="luxury",
            firm_area="social",
            product=[f"Social_{i}" for i in range(n_social)],
            production_capacity=[random.randint(150, 400) for _ in range(n_social)],
            profit_margin=0.40,
            production_cost=[random.uniform(60.0, 120.0) for _ in range(n_social)],
            entry_wage=[random.randint(50000, 65000) for _ in range(n_social)],
            num_employees=[random.randint(8, 40) for _ in range(n_social)],
            production_level=[random.uniform(0.5, 0.9) for _ in range(n_social)]
        )
        
        # Analytical firms (finance, data analysis) - 15 firms
        n_analytical = 5
        FirmAgent.create_agents(
            model=self,
            n=n_analytical,
            firm_type="luxury",
            firm_area="analytical",
            product=[f"Analytical_{i}" for i in range(n_analytical)],
            production_capacity=[random.randint(100, 350) for _ in range(n_analytical)],
            profit_margin=0.50,
            production_cost=[random.uniform(80.0, 150.0) for _ in range(n_analytical)],
            entry_wage=[random.randint(65000, 85000) for _ in range(n_analytical)],
            num_employees=[random.randint(5, 25) for _ in range(n_analytical)],
            production_level=[random.uniform(0.6, 0.9) for _ in range(n_analytical)]
        )


        n_households = 2000
        HouseholdAgent.create_agents(
            model=self,
            n=n_households,
            num_people=[random.randint(1, 5) for _ in range(n_households)],
            spend_ratio=[round(random.uniform(0.4, 1.0), 2) for _ in range(n_households)],
            income_tax_rate=0.15  # TODO: Same for all for now, so one value is fine
        )

        

    def step(self):
        self.datacollector.collect(self)        
        self.agents.do("step")
