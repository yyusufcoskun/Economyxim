import mesa
import numpy as np
import pandas as pd
import random

class IntermediaryFirmAgent(mesa.Agent):
    def __init__(self, model, initial_employee_target=240):
        super().__init__(model)
        self.employees = []
        self.num_employees = 0

        self.demand_received_from_firms = 0
        self.revenue = 0
        self.capital = 0

        self.skill_types_to_hire = ["physical", "service", "technical", "creative", "social", "analytical"]

        self._populate_initial_workforce(initial_employee_target)

    def _populate_initial_workforce(self, target_total_employees):
        """
        Hires the initial set of employees, aiming for an equal number from each skill type.
        All hired as 'entry' level. Skill level value is not a criterion.
        Wages are initialized to 0 and set dynamically in the step method.
        """
        # print(f"[DEBUG] IntermediaryFirm {self.unique_id}: Populating initial workforce. Target: {target_total_employees}")
        if not hasattr(self.model, 'available_persons') or not self.model.available_persons:
            print(f"[WARNING] IntermediaryFirm {self.unique_id}: No available persons for initial workforce.")
            return

        if not self.skill_types_to_hire:
            print(f"[WARNING] IntermediaryFirm {self.unique_id}: No skill types defined for hiring.")
            return

        num_skill_categories = len(self.skill_types_to_hire)
        if num_skill_categories == 0: return

        num_to_hire_per_skill_type = round(target_total_employees / num_skill_categories)
        # print(f"[DEBUG] IntermediaryFirm {self.unique_id}: Targeting {num_to_hire_per_skill_type} per skill type.")
        
        total_hired_count = 0

        for skill_type in self.skill_types_to_hire:
            if total_hired_count >= target_total_employees:
                break
            
            # print(f"[DEBUG] IntermediaryFirm {self.unique_id}: Attempting to hire for skill type '{skill_type}'.")
            hired_for_this_skill_type = 0
            
            # Iterate over a copy for safe processing if needed, though not removing from global list here
            possible_hires = []
            for p in list(self.model.available_persons):
                if p.job_seeking is True and p.employer is None and p.skill_type == skill_type:
                    possible_hires.append(p)
            random.shuffle(possible_hires)

            for candidate_idx, candidate in enumerate(possible_hires):
                if hired_for_this_skill_type >= num_to_hire_per_skill_type or total_hired_count >= target_total_employees:
                    break

                if candidate.employer is None and candidate.job_seeking is True:
                    candidate.employer = self
                    candidate.job_seeking = False
                    candidate.job_level = "entry"
                    candidate.wage = 0 
                    
                    self.employees.append(candidate)
                    self.num_employees += 1
                    total_hired_count += 1
                    hired_for_this_skill_type +=1
                    # print(f"[DEBUG] IntermediaryFirm {self.unique_id}: Hired Person {candidate.unique_id} for skill '{skill_type}'. Total hired: {self.num_employees}")
                # else:
                    # print(f"[DEBUG] IntermediaryFirm {self.unique_id}: Candidate {candidate.unique_id} for skill '{skill_type}' was already hired or not seeking.")

            # print(f"[DEBUG] IntermediaryFirm {self.unique_id}: Hired {hired_for_this_skill_type} for skill '{skill_type}'.")
            
        print(f"[INFO] IntermediaryFirm {self.unique_id}: Initial workforce. Target: {target_total_employees}, Actual Hired: {self.num_employees}")

    def receive_firm_demand(self, cost):
        """Record demand received from firms."""
        self.demand_received_from_firms += cost

    def step(self):
        self.revenue = self.demand_received_from_firms
        
        if self.num_employees > 0:
            wage_per_employee = self.revenue / self.num_employees
        else:
            wage_per_employee = 0
        
        # print(f"[DEBUG] IntermediaryFirm {self.unique_id} Step: Revenue: {self.revenue:.2f}, Employees: {self.num_employees}, Wage per Employee: {wage_per_employee:.2f}")

        for person_idx, person in enumerate(self.employees):
            person.wage = wage_per_employee
            # if person_idx < 2: # Log for first few employees
                # print(f"[DEBUG] IntermediaryFirm {self.unique_id}: Set Person {person.unique_id} wage to {person.wage:.2f}")
            
        self.demand_received_from_firms = 0
