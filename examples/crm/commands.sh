#!/usr/bin/env bash
# ---------------------------------------------------------------------------
# Laravel & Filament Artisan Commands for: Apex CRM
# Generated deterministically from spec.json
# NOTE: Dry-run inspection only. Review before running in production.
# ---------------------------------------------------------------------------
set -euo pipefail

echo "==> Starting Artisan scaffolding for Apex CRM..."

# Step 1: Filament Panels
php artisan make:filament-panel sales

# Step 2: Enums
php artisan make:enum UserRoleEnum
php artisan make:enum ActivityTypeEnum

# Step 3: Eloquent Models & Migrations (-mfsc)
php artisan make:model User -mfsc
php artisan make:model Company -mfsc
php artisan make:model AuditLog -mfsc
php artisan make:model Contact -mfsc
php artisan make:model Deal -mfsc
php artisan make:model Activity -mfsc
php artisan make:model Note -mfsc

# Step 4: Authorization Policies
php artisan make:policy UserPolicy --model=User
php artisan make:policy CompanyPolicy --model=Company
php artisan make:policy ContactPolicy --model=Contact
php artisan make:policy DealPolicy --model=Deal
php artisan make:policy ActivityPolicy --model=Activity
php artisan make:policy NotePolicy --model=Note
php artisan make:policy AuditLogPolicy --model=AuditLog

# Step 5: Filament Resources
php artisan make:filament-resource User
php artisan make:filament-resource Company
php artisan make:filament-resource Contact
php artisan make:filament-resource Deal
php artisan make:filament-resource Activity
php artisan make:filament-resource Note
php artisan make:filament-resource AuditLog
php artisan make:filament-resource Company --panel=sales
php artisan make:filament-resource Contact --panel=sales
php artisan make:filament-resource Deal --panel=sales
php artisan make:filament-resource Activity --panel=sales
php artisan make:filament-resource Note --panel=sales

echo "==> Artisan scaffolding completed successfully."
