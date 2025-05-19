import mesa
import numpy as np
import pandas as pd
import random
from agents import GovernmentAgent
from agents import FirmAgent
from agents import HouseholdAgent
from agents import IntermediaryFirmAgent
from agents import PersonAgent


class EconomicSimulationModel(mesa.Model):
    def __init__(self):
        super().__init__()
        
        # Initialize step counter
        self.current_step = 0
        self.available_persons = []
        self.num_persons = 30000

        self.datacollector = mesa.DataCollector(
            model_reporters={
                "Reserves": lambda m: m.government_agent.reserves,
                "Step Public Spending": lambda m: m.government_agent.step_public_spending,
                "Unemployment Rate": lambda m: m.government_agent.unemployment_rate,
                "GDP": lambda m: m.government_agent.GDP,
                "Tax Revenue": lambda m: m.government_agent.step_tax_revenue,
                "Inflation Rate": lambda m: m.government_agent.inflation_rate,
                "Gini Coefficient": lambda m: m.government_agent.gini_coefficient,
            },
            agent_reporters= {
                 # Firm agent fields
                "FirmType": lambda a: getattr(a, "firm_type", None),
                "FirmArea": lambda a: getattr(a, "firm_area", None),
                "Profit": lambda a: getattr(a, "profit", None),
                "Inventory": lambda a: getattr(a, "inventory", None),
                "ProductPrice": lambda a: getattr(a, "product_price", None),
                "RevenuePerEmployee": lambda a: getattr(a, "revenue_per_employee", None),
                "ProductionLevel": lambda a: getattr(a, "production_level", None),
                "NumEmployees": lambda a: getattr(a, "num_employees", None),
                "DemandReceived": lambda a: getattr(a, "demand_for_tracking", None),
                "InventoryDemandRatio": lambda a: getattr(a, "inventory_demand_ratio", None),
                "SellThroughRate": lambda a: getattr(a, "sell_through_rate", None),
                "ProductionCapacity": lambda a: getattr(a, "production_capacity", None),
                "Revenue": lambda a: getattr(a, "revenue", None),
                "Costs": lambda a: getattr(a, "costs", None),
                "Markup": lambda a: getattr(a, "markup", None),
                "ProducedUnits": lambda a: getattr(a, "produced_units", None),
                "UnmetDemand": lambda a: getattr(a, "unmet_demand", None),
                "Capital": lambda a: getattr(a, "capital", None),
                

                # Household agent fields
                "IncomeBracket": lambda a: getattr(a, "income_bracket", None),
                "WealthBracket": lambda a: getattr(a, "wealth_bracket", None),
                "NumPeople": lambda a: getattr(a, "num_people", None),
                "HouseholdStepIncome": lambda a: getattr(a, "household_step_income", None),
                "HouseholdStepIncomePostTax": lambda a: getattr(a, "household_step_income_posttax", None),
                "HouseholdStepExpense": lambda a: getattr(a, "household_step_expense", None),
                "HouseholdStepSavings": lambda a: getattr(a, "household_step_savings", None),
                "TotalHouseholdSavings": lambda a: getattr(a, "total_household_savings", None),
                "HealthLevel": lambda a: getattr(a, "health_level", None),
                "Welfare": lambda a: getattr(a, "welfare", None),
                "DebtLevel": lambda a: getattr(a, "debt_level", None),
                "IncomeTaxRate": lambda a: getattr(a, "income_tax_rate", None),
                "NumWorkingPeople": lambda a: getattr(a, "num_working_people", None),
                "NumNotSeekingJob": lambda a: getattr(a, "num_not_seeking_job", None),
                "NumSeekingJob": lambda a: getattr(a, "num_seeking_job", None),
                
                # Person agent fields
                "SkillLevel": lambda a: getattr(a, "skill_level", None),
                "SkillType": lambda a: getattr(a, "skill_type", None),
                "JobLevel": lambda a: getattr(a, "job_level", None),
                "IsEmployed": lambda a: 1 if getattr(a, "employer", None) is not None else 0,
                "Wage": lambda a: getattr(a, "wage", None),
                "JobSeeking": lambda a: getattr(a, "job_seeking", None),
                "Labor": lambda a: getattr(a, "labor", None),
            }
        )
        
        self.government_agent = GovernmentAgent.create_agents(model=self, n=1)[0]
        
        # print(f"[DEBUG] EconomicSimulationModel: Initializing {self.num_persons} PersonAgents.")
        for i in range(self.num_persons):
            person = PersonAgent(model=self)
            self.available_persons.append(person)
        # print(f"[DEBUG] EconomicSimulationModel: Created {len(self.schedule.agents)} total agents after PersonAgent init, {len(self.available_persons)} available persons.")

        # Create firms with different areas and suitable parameters
        
        # --- NECESSITY FIRMS ---
        
        # Physical firms (manufacturing, construction, farming) - 25 firms
        n_physical = 30
        FirmAgent.create_agents(
            model=self,
            n=n_physical,
            firm_type="necessity",
            firm_area="physical",
            product=[f"Physical_{i}" for i in range(n_physical)],
            production_capacity=[random.randint(12000, 18000) for _ in range(n_physical)],
            markup=2,
            production_cost=[random.uniform(1.8, 3.5) for _ in range(n_physical)],
            entry_wage=[random.randint(60000, 75000) for _ in range(n_physical)],
            initial_employee_target=[random.randint(30, 120) for _ in range(n_physical)],
            #production_level=[random.uniform(0.7, 1) for _ in range(n_physical)]
        )
        
        # Service firms (retail, food service, basic services) - 30 firms
        n_service = 30
        FirmAgent.create_agents(
            model=self,
            n=n_service,
            firm_type="necessity",
            firm_area="service",
            product=[f"Service_{i}" for i in range(n_service)],
            production_capacity=[random.randint(9000, 21000) for _ in range(n_service)],
            markup=3,
            production_cost=[random.uniform(1.5, 3.5) for _ in range(n_service)],
            entry_wage=[random.randint(54000, 66000) for _ in range(n_service)],
            initial_employee_target=[random.randint(15, 50) for _ in range(n_service)],
            #production_level=[random.uniform(0.6, 0.9) for _ in range(n_service)]
        )
        
        # --- LUXURY FIRMS ---
        
        # Technical firms (tech companies, engineering) - 10 firms
        n_technical = 10
        FirmAgent.create_agents(
            model=self,
            n=n_technical,
            firm_type="luxury",
            firm_area="technical",
            product=[f"Technical_{i}" for i in range(n_technical)],
            production_capacity=[random.randint(900, 2100) for _ in range(n_technical)],
            markup=7,
            production_cost=[random.uniform(50.0, 150.0) for _ in range(n_technical)],
            entry_wage=[random.randint(180000, 225000) for _ in range(n_technical)],
            initial_employee_target=[random.randint(10, 80) for _ in range(n_technical)],
            #production_level=[random.uniform(0.5, 0.9) for _ in range(n_technical)]
        )
        
        # Creative firms (design, arts, media) - 5 firms
        n_creative = 5
        FirmAgent.create_agents(
            model=self,
            n=n_creative,
            firm_type="luxury",
            firm_area="creative",
            product=[f"Creative_{i}" for i in range(n_creative)],
            production_capacity=[random.randint(600, 1500) for _ in range(n_creative)],
            markup=6,
            production_cost=[random.uniform(40.0, 80.0) for _ in range(n_creative)],
            entry_wage=[random.randint(135000, 180000) for _ in range(n_creative)],
            initial_employee_target=[random.randint(5, 30) for _ in range(n_creative)],
            #production_level=[random.uniform(0.4, 0.8) for _ in range(n_creative)]
        )
        
        # Social firms (management consulting, education) - 5 firms
        n_social = 5
        FirmAgent.create_agents(
            model=self,
            n=n_social,
            firm_type="luxury",
            firm_area="social",
            product=[f"Social_{i}" for i in range(n_social)],
            production_capacity=[random.randint(450, 1200) for _ in range(n_social)],
            markup=5,
            production_cost=[random.uniform(60.0, 100.0) for _ in range(n_social)],
            entry_wage=[random.randint(150000, 195000) for _ in range(n_social)],
            initial_employee_target=[random.randint(8, 40) for _ in range(n_social)],
            #production_level=[random.uniform(0.5, 0.9) for _ in range(n_social)]
        )
        
        # Analytical firms (finance, data analysis) - 5 firms
        n_analytical = 5
        FirmAgent.create_agents(
            model=self,
            n=n_analytical,
            firm_type="luxury",
            firm_area="analytical",
            product=[f"Analytical_{i}" for i in range(n_analytical)],
            production_capacity=[random.randint(300, 1000) for _ in range(n_analytical)],
            markup=6,
            production_cost=[random.uniform(80.0, 150.0) for _ in range(n_analytical)],
            entry_wage=[random.randint(165000, 215000) for _ in range(n_analytical)],
            initial_employee_target=[random.randint(5, 25) for _ in range(n_analytical)],
            #production_level=[random.uniform(0.6, 0.9) for _ in range(n_analytical)]
        )

        # --- INTERMEDIARY FIRM ---

        n_intermediary = 1
        IntermediaryFirmAgent.create_agents(
            model=self,
            n=n_intermediary,
            initial_employee_target=240
        )

        n_households = 1000
        HouseholdAgent.create_agents(
            model=self,
            n=n_households,
            num_people=[random.randint(1, 5) for _ in range(n_households)],
            income_tax_rate=0.15  
        )

        self._assign_persons_to_households()

        # Step 6: Cleanup Unassigned PersonAgents
        # print(f"[DEBUG] EconomicSimulationModel: Total agents in scheduler before cleanup: {len(self.agents)}.")

        persons_to_remove = list(self.available_persons) 
        removed_count = 0
        actually_removed_from_schedule_count = 0

        # print(f"[DEBUG] EconomicSimulationModel: Cleanup - Iterating through {len(persons_to_remove)} persons found in available_persons list.")

        for person in persons_to_remove:
            # NEW CRITERIA: Any person who is not in a household by this stage should be removed.
            # This includes employed persons who didn't get a household, and unemployed who didn't.
            if person.household is None:
                # print(f"[DEBUG] EconomicSimulationModel: Removing Person {person.unique_id} (Employer: {person.employer is not None}, Household: {person.household is None}) because they are not in a household.")
                try:
                    self.agents.remove(person) # Remove from scheduler
                    actually_removed_from_schedule_count += 1
                except ValueError:
                    #print(f"[DEBUG] EconomicSimulationModel: Person {person.unique_id} already removed from schedule or not found.")
                    pass

                if hasattr(self, 'agents') and person in self.agents:
                    try:
                        self.agents.remove(person) 
                    except ValueError:
                        pass 

                # Remove from our temporary tracking list `available_persons`
                if person in self.available_persons:
                     self.available_persons.remove(person)
                removed_count +=1 
            # else:
                # print(f"[DEBUG] EconomicSimulationModel: Person {person.unique_id} is in a household. Not removing from simulation.")
        
        print(f"[DEBUG] EconomicSimulationModel: Finished cleanup. Iterated {len(persons_to_remove)} from available_persons initially.")
        print(f"[DEBUG] EconomicSimulationModel: Removed {removed_count} persons from available_persons list based on household status.")
        print(f"[DEBUG] EconomicSimulationModel: Attempted to remove {actually_removed_from_schedule_count} persons from schedule.")
        print(f"[DEBUG] EconomicSimulationModel: {len(self.available_persons)} persons remaining in available_persons list (should be 0).")
        print(f"[DEBUG] EconomicSimulationModel: Total agents in scheduler after cleanup: {len(self.agents)}.") # Use self.schedule.agents for scheduler count


    def _assign_persons_to_households(self):
        """
        Assigns persons to households with a strategy to ensure employed persons are
        housed and to promote heterogeneity within households.
        """
        if not hasattr(self, 'available_persons'):
            print("[ERROR] _assign_persons_to_households: self.available_persons not found.")
            return

        employed_to_place = [p for p in self.available_persons if p.employer is not None and p.household is None]
        unemployed_to_place = [p for p in self.available_persons if p.employer is None and p.household is None]

        random.shuffle(employed_to_place)
        random.shuffle(unemployed_to_place)

        all_households = [h for h in self.agents if isinstance(h, HouseholdAgent)]
        random.shuffle(all_households)

        print(f"[INFO] Assigning persons: Initial - {len(employed_to_place)} employed, {len(unemployed_to_place)} unemployed. {len(all_households)} households.")

        # Iteratively distribute employed persons, one per household per pass
        # print("[INFO] Distributing employed persons...")
        placed_in_a_pass = True # Flag to continue passes if someone was placed
        while employed_to_place and placed_in_a_pass:
            placed_in_this_pass = False
            # Iterate over a copy of all_households in case its order needs to be stable for a pass, or shuffled each pass
            # For fairness, shuffling each pass might be better if some households fill up.
            random.shuffle(all_households) 
            for hh in all_households:
                if not employed_to_place: # All employed persons have been placed
                    break
                if hh.current_population < hh.num_people:
                    person = employed_to_place.pop(0)
                    hh.members.append(person)
                    person.household = hh
                    hh.current_population += 1
                    if person in self.available_persons: # Should always be true as employed_to_place is from available_persons
                        self.available_persons.remove(person)
                    placed_in_this_pass = True
                    # print(f"[DEBUG] Assigned Employed {person.unique_id} to HH {hh.unique_id} (Pop: {hh.current_population}/{hh.num_people})")
            
            placed_in_a_pass = placed_in_this_pass # Continue if at least one person was placed in the full pass

        if employed_to_place: # Should only happen if no households have space left
            for person in employed_to_place:
                 print(f"[ERROR] EconomicSimulationModel: Could not place employed Person {person.unique_id} (Employer: {person.employer.unique_id if person.employer else 'None'}) in any household due to lack of overall capacity. This person may be removed if unhoused.")
                 # These persons remain in employed_to_place (and thus were in available_persons and not removed)
                 # and their person.household is None. The cleanup step will handle them.

        # print(f"[INFO] Distributing unemployed persons... {len(unemployed_to_place)} remaining.")
        # Distribute unemployed persons into remaining spots
        random.shuffle(all_households) # Shuffle again before distributing unemployed
        for hh in all_households:
            while hh.current_population < hh.num_people and unemployed_to_place:
                person = unemployed_to_place.pop(0)
                hh.members.append(person)
                person.household = hh
                hh.current_population += 1
                if person in self.available_persons: # Should always be true
                    self.available_persons.remove(person)
                # print(f"[DEBUG] Assigned Unemployed {person.unique_id} to HH {hh.unique_id} (Pop: {hh.current_population}/{hh.num_people})")

        # Final step: update employment counts for all households
        for hh_agent in all_households:
            if hasattr(hh_agent, '_update_employment_counts'):
                hh_agent._update_employment_counts()
            # print(f"[DEBUG] HH {hh_agent.unique_id}: Pop {hh_agent.current_population}/{hh_agent.num_people}. Employed: {hh_agent.num_working_people}")
        
        print(f"[INFO] Person assignment complete. {len(self.available_persons)} persons remain unassigned (these will be cleaned up if household is None).")
        
    def step(self):
        # Initialize counter for unmet necessity households at the start of each step
        self.unmet_necessity_households_count = 0
        
        # Step 1: Government Agent acts first
        self.government_agent.step()
        
        # Step 2: Household Agents act (to generate demand for the current step)
        household_agents = [agent for agent in self.agents if isinstance(agent, HouseholdAgent)]
        for agent in household_agents:
            agent.step()
            
        # Step 3: Firm Agents act (processing demand from Gov & Households from current step)
        firm_agents = [agent for agent in self.agents if isinstance(agent, FirmAgent)]
        for agent in firm_agents:
            agent.step()

        # Step 4: Intermediary Firm Agents act (processing demand from Firms from current step)
        intermediary_firm_agents = [agent for agent in self.agents if isinstance(agent, IntermediaryFirmAgent)]
        for agent in intermediary_firm_agents:
            agent.step()

        # Step 5: Person Agents act (skill updates, job seeking logic)
        person_agents = [agent for agent in self.agents if isinstance(agent, PersonAgent)]
        for agent in person_agents:
            agent.step()
            
        # Step 6: Collect data after all agents have completed their actions for the current step
        self.datacollector.collect(self)
        
        # Find the highest capital value among all firms (can be part of datacollection if needed often)
        highest_capital = 0
        for agent in self.agents: # Iterate through all agents, not just firms, if capital can exist elsewhere
            if hasattr(agent, 'capital') and agent.capital is not None and agent.capital > highest_capital:
                highest_capital = agent.capital
        
        # Step 7: Increment step counter
        self.current_step += 1
        
        # Optional: Print step summary information
        print(f"[INFO] Step {self.current_step}: Households not meeting necessity goal: {self.unmet_necessity_households_count}")
        print(f"[DEBUG] Step {self.current_step} completed | Highest Capital: {highest_capital:.2f}")
