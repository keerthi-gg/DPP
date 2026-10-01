# Product Specification

## Vision

Create a Digital Product Passport (DPP) platform for plastic products that improves traceability, accountability, and circular economy participation.

## Problem statement

Current plastic lifecycle systems lack reliable proof that materials are actually collected, reused, or recycled. QR scans and manual reporting are easy to manipulate, which undermines trust and limits win-win sustainability outcomes.

## Goals

- Give every product a unique digital identity
- Link product lifecycle events to verifiable payments or transactions
- Enable transparent stakeholder visibility across supply chains
- Support recycling incentives for consumers and collection centers
- Generate compliance and sustainability reporting data

## Core user roles

- Manufacturer
- Distributor or retailer
- Consumer
- Waste collector or recycler
- Regulator or compliance viewer

## Functional requirements

1. Product registration
   - Manufacturers can create a DPP for a plastic item
   - The product receives a unique QR-based identity reference

2. Product lookup
   - Stakeholders can scan or query a product using the QR code or DPP ID

3. Lifecycle tracking
   - Product lifecycle stages are recorded in order
   - States include manufactured, in transit, returned, recycled, and closed

4. Payment-linked validation
   - Product updates are tied to verified financial or token actions
   - Smart-contract logic validates lifecycle events

5. Consumer reward flow
   - Users receive rewards when valid recycling activity is confirmed

6. Reporting
   - Verified transactions feed compliance and ESG reporting views

## Non-functional requirements

- Secure identity and transaction records
- Easy stakeholder onboarding
- API-first integration for future apps and services
- Scalable architecture for later blockchain or microservice expansion

## Success criteria

- Product data can be created and queried
- Lifecycle changes can be validated via backend logic
- The system provides a minimal working MVP for DPP tracking
