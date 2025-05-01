import mesa
import numpy as np
import pandas as pd
import random


class PersonAgent(mesa.Agent):
    """
        Initialize a person agent.
        Args:
            household: The household this person belongs to
            employer: The firm that employs this person (None if unemployed)
            skill_type: skill type this person has (e.g. "technical", "physical", etc.)
            job_seeking: Whether this person is actively looking for work
            wage: Current wage/salary of the person
            work_hours: Preferred hours worked per week
        """
    def __init__(self, model, household, job_seeking=True, wage=0, work_hours=40):
        super().__init__(model)

        self.household = household
        self.employer = None
        
        skill_types = ["physical", "service", "technical", "creative", "social", "analytical"]
        self.skill_type = random.choice(skill_types)
        
        self.job_seeking = job_seeking
        self.wage = wage
        self.work_hours = work_hours
        
        # Generate a more realistic skill distribution (normal distribution centered around 40-60)
        self.skill_level = min(100, max(1, random.normalvariate(50, 15)))  # Normal distribution with mean 50, std 15
        
        # Job level (senior, mid, entry) - will be set when hired
        self.job_level = None
        
        self.unemployed_counter = 0  # Track how many steps person has been unemployed
        self.study_cooldown = 0  # Track remaining study period when person stops looking
        
        # Initial skill improvement rate (0.2% per step)
        self.skill_improvement_rate = 0.001
        
    def step(self):
        '''
        # Improve skills if employed
        if self.employer is not None:
            self.skill_level = min(100, self.skill_level * (1 + self.skill_improvement_rate))
            
        # Handle unemployment and skill improvement through study
        elif self.job_seeking:
            self.unemployed_counter += 1

            # If unemployed for too long, take a break to study
            if self.unemployed_counter >= 4:  #  threshold before giving up
                self.job_seeking = False
                self.study_cooldown = 2  # Study for 2 steps
                self.unemployed_counter = 0
                
        # If in study period, improve skills and track cooldown        
        elif self.study_cooldown > 0:
            self.skill_level = min(100, self.skill_level * (1 + self.skill_improvement_rate * 1.5))
            self.study_cooldown -= 1
            
            # Resume job seeking after study period
            if self.study_cooldown == 0:
                self.job_seeking = True
                
            # If employed, should not be job seeking
            if self.employer is not None:
                self.job_seeking = False
        '''

