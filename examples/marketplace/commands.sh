#!/usr/bin/env bash
# ---------------------------------------------------------------------------
# Laravel & Filament Artisan Commands for: Marketplace Pro
# Generated deterministically from spec.json
# NOTE: Dry-run inspection only. Review before running in production.
# ---------------------------------------------------------------------------
set -euo pipefail

echo "==> Starting Artisan scaffolding for Marketplace Pro..."

# Step 1: Filament Panels
php artisan make:filament-panel vendor

# Step 2: Enums
php artisan make:enum ProductStatusEnum

# Step 3: Eloquent Models & Migrations (-mfsc)
php artisan make:model User -mfsc
php artisan make:model Category -mfsc
php artisan make:model VendorProfile -mfsc
php artisan make:model Order -mfsc
php artisan make:model Product -mfsc
php artisan make:model Payment -mfsc
php artisan make:model OrderItem -mfsc
php artisan make:model Review -mfsc

# Step 4: Authorization Policies
php artisan make:policy UserPolicy --model=User
php artisan make:policy VendorProfilePolicy --model=VendorProfile
php artisan make:policy CategoryPolicy --model=Category
php artisan make:policy ProductPolicy --model=Product
php artisan make:policy OrderPolicy --model=Order
php artisan make:policy OrderItemPolicy --model=OrderItem
php artisan make:policy PaymentPolicy --model=Payment
php artisan make:policy ReviewPolicy --model=Review

# Step 5: Filament Resources
php artisan make:filament-resource User
php artisan make:filament-resource VendorProfile
php artisan make:filament-resource Category
php artisan make:filament-resource Product
php artisan make:filament-resource Order
php artisan make:filament-resource Payment
php artisan make:filament-resource Review
php artisan make:filament-resource VendorProfile --panel=vendor
php artisan make:filament-resource Product --panel=vendor
php artisan make:filament-resource Order --panel=vendor

echo "==> Artisan scaffolding completed successfully."
