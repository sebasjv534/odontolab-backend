"""
Enumerations for the OdontoLab system.

This module defines all enum types used across the application,
providing type safety and standardization for categorical data.
"""

from enum import Enum


class Gender(str, Enum):
    """
    Gender enumeration for patient records.
    
    Provides standardized gender options while respecting privacy preferences.
    """
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"
    PREFER_NOT_TO_SAY = "prefer_not_to_say"


class InterventionType(str, Enum):
    """
    Types of dental interventions.
    
    Comprehensive list of dental procedures supported by the system.
    Used for categorizing treatments and generating reports.
    """
    CONSULTATION = "consultation"
    CLEANING = "cleaning"
    FILLING = "filling"
    EXTRACTION = "extraction"
    ROOT_CANAL = "root_canal"
    CROWN = "crown"
    BRIDGE = "bridge"
    IMPLANT = "implant"
    ORTHODONTICS = "orthodontics"
    SURGERY = "surgery"
    EMERGENCY = "emergency"
    OTHER = "other"
