import mesa
import numpy as np
import pandas as pd
import random

class IntermediaryFirmAgent(mesa.Agent):
    '''
    Represents an intermediary firm that connects production firms with raw materials.
    
    This agent acts as a supplier to other firms in the economy, receiving demand and 
    revenue from them and redistributing this revenue to its employees. It serves as 
    a mechanism to complete the economic cycle by channeling money from production firms
    back to households through wages paid to its employees.
    '''
    def __init__(self, model, initial_employee_target=240):
        '''
        Initialize a new intermediary firm with workforce parameters.
        
        Parameters:
        - model: Mesa model instance the agent belongs to
        - initial_employee_target: Target number of initial employees to hire
        '''
        super().__init__(model)
        self.employees = []
        self.num_employees = 0

        self.demand_received_from_firms = 0
        self.revenue = 0
        self.capital = 0

        self.skill_types_to_hire = ["physical", "service", "technical", "creative", "social", "analytical"]

        self._populate_initial_workforce(initial_employee_target)

    def _populate_initial_workforce(self, target_total_employees):
        '''
        Hire the initial set of employees for the intermediary firm.
        
        This method aims to hire an equal number of employees from each skill type.
        All employees are hired at entry level, with wages initially set to zero.
        Wages will be determined dynamically during each step based on the firm's revenue.
        
        Parameters:
        - target_total_employees: Desired number of total employees to hire
        '''
        
        if not hasattr(self.model, 'available_persons') or not self.model.available_persons:
            print(f"[WARNING] IntermediaryFirm {self.unique_id}: No available persons for initial workforce.")
            return

        if not self.skill_types_to_hire:
            print(f"[WARNING] IntermediaryFirm {self.unique_id}: No skill types defined for hiring.")
            return

        num_skill_categories = len(self.skill_types_to_hire)
        if num_skill_categories == 0: return

        # Calculate target hires per skill type to achieve balanced workforce
        num_to_hire_per_skill_type = round(target_total_employees / num_skill_categories)
        
        total_hired_count = 0

        # Hire workers for each skill type
        for skill_type in self.skill_types_to_hire:
            if total_hired_count >= target_total_employees:
                break
            
            hired_for_this_skill_type = 0
            
            # Find candidates with matching skill type
            possible_hires = []
            for p in list(self.model.available_persons):
                if p.job_seeking is True and p.employer is None and p.skill_type == skill_type:
                    possible_hires.append(p)
            random.shuffle(possible_hires)

            # Hire candidates until target for this skill type is reached
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
            
        print(f"[INFO] IntermediaryFirm {self.unique_id}: Initial workforce. Target: {target_total_employees}, Actual Hired: {self.num_employees}")

    def receive_firm_demand(self, cost):
        '''
        Record demand and payment received from production firms.
        
        This method is called by production firms when they spend money on raw materials.
        The payment accumulates as revenue for the intermediary firm, which will be
        distributed to its employees as wages during the step method.
        
        Parameters:
        - cost: The amount of money received from a production firm
        '''
        
        self.demand_received_from_firms += cost

    def step(self):
        '''
        Execute one step of the intermediary firm's operations.
        
        This method handles the intermediary firm's financial cycle:
        1. Sets revenue equal to the accumulated demand from production firms
        2. Calculates wage per employee by evenly distributing revenue
        3. Updates each employee's wage
        4. Resets demand for the next step
        
        The intermediary firm acts as a channel to return money spent by production 
        firms back to households via wages, completing the economic flow.
        '''
        
        # Set revenue based on accumulated demand from firms
        self.revenue = self.demand_received_from_firms
        
        # Calculate wage per employee based on total revenue
        if self.num_employees > 0:
            wage_per_employee = self.revenue / self.num_employees
        else:
            wage_per_employee = 0

        # Distribute revenue equally among all employees as wages
        for person_idx, person in enumerate(self.employees):
            person.wage = wage_per_employee
            
        # Reset demand tracker for the next step
        self.demand_received_from_firms = 0
