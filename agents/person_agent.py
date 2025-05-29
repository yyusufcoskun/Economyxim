import mesa
import numpy as np
import pandas as pd
import random


class PersonAgent(mesa.Agent):
    '''
    Represents an individual person in the economic simulation.
    
    This agent can be employed by firms, possess skills, and seek employment.
    Persons belong to households and contribute to household income through
    wages earned from employment. They have different skill types and levels
    that determine their suitability for various jobs.
    '''
    def __init__(self, model, job_seeking=True, wage=0, work_hours=40):
        '''
        Initialize a person agent with employment characteristics and skills.
        
        Parameters:
        - model: The main simulation model
        - job_seeking: Whether the person is actively looking for work
        - wage: Current wage/salary of the person
        - work_hours: Preferred hours worked per week
        '''
        super().__init__(model)

        self.household = None # Will be set by HouseholdAgent
        self.employer = None
        
        skill_types = ["physical", "service", "technical", "creative", "social", "analytical"]
        self.skill_type = random.choice(skill_types)
        
        self.job_seeking = job_seeking
        self.wage = wage
        self.work_hours = work_hours
        
        # Generate a more realistic skill distribution (normal distribution centered around 40-60)
        self.skill_level = min(100, max(1, random.normalvariate(50, 15)))  # Normal distribution with mean 50, std 15
        self.labor = self.skill_level/random.uniform(3, 5)
        
        # Job level (senior, mid, entry) - will be set when hired
        self.job_level = None
        
        self.unemployed_counter = 0  # Track how many steps person has been unemployed
        self.study_cooldown = 0  # Track remaining study period when person stops looking
        
        # Initial skill improvement rate (0.2% per step)
        self.skill_improvement_rate = 0.001
        
        # Flag to track if the person is currently studying due to low skills
        self.studying_for_min_skills = False
        
    def step(self):
        '''
        Execute one step of the person agent's life cycle.
        
        This method handles the person's employment status, skill development,
        and job-seeking behavior. Key activities include:
        - Determining if the person needs to study to reach minimum skill requirements
        - Increasing skill levels through study
        - Managing job-seeking status based on employment and study status
        
        The step method is called by the model scheduler at each simulation step.
        '''
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

        # Check if skill level is below entry level for their skill type
        min_entry_level = 10  # Default fallback value
        
        # Find any firm to get the configuration
        for agent in self.model.agents:
            if hasattr(agent, 'min_skill_levels_config'):
                # Get the minimum entry level skill for this person's skill type
                if self.skill_type in agent.min_skill_levels_config:
                    min_entry_level = agent.min_skill_levels_config[self.skill_type]["entry"]
                break
        
        # If currently studying for minimum skills or job seeking but below threshold
        if self.studying_for_min_skills or (self.job_seeking and self.skill_level < min_entry_level):
            self.studying_for_min_skills = True
            self.job_seeking = False
            
            # Study more intensively to reach minimum requirements
            self.skill_level = min(100, self.skill_level * (1 + self.skill_improvement_rate * 1.5))
            
            # Check if reached minimum skill level
            if self.skill_level >= min_entry_level:
                self.studying_for_min_skills = False
                self.job_seeking = True
        
        # If employed, should not be job seeking
        if self.employer is not None:
            self.job_seeking = False
            self.studying_for_min_skills = False



        

