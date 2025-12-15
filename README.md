# ESU Performance Tester

## Overview
The **Electrosurgical Unit (ESU) Testing System** is a tool designed to simulate and evaluate the performance of Electrosurgical Units (ESUs) used in medical environments. It ensures that ESUs are performing within safe parameters for both power accuracy and leakage current. This system was developed using **Streamlit** for a user-friendly web interface and includes logic based on the IEC 60601-2-2 standard.

The tool simulates essential tests, providing immediate feedback on whether the ESU passes or fails, with detailed diagnostics for engineers to make informed decisions.

## Key Features
- **Power Output Calculation**: Ensures the set power matches the delivered power.
- **Leakage Current Measurement**: Validates that leakage current stays within the safe limit.
- **Pass/Fail Evaluation**: The system displays whether the ESU passes or fails the test based on power and leakage thresholds.
- **Detailed Metrics**: Provides specific measurements of power, leakage, and load resistance with real-time updates.
- **Regulatory Compliance**: Follows IEC 60601-2-2 standards for medical device safety.

## Installation
To use the ESU Performance Tester, you need to have Python installed on your system. Follow the steps below to set up the environment:

1. Clone the repository:
   ```bash
   git clone https://github.com/mohamedhossam15/ESU-Performance-Tester.git
   cd ESU-Performance-Tester
