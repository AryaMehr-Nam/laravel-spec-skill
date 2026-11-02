# Database Schema & Data Models

This document details the database schema, column types, and relationships.

## Tables Overview

| Model | Table | Primary Key | Foreign References |
| :--- | :--- | :--- | :--- |
| **User** | `users` | `id` (bigInteger) | None |
| **VendorProfile** | `vendor_profiles` | `id` (bigInteger) | `user_id -> User` |
| **Category** | `categories` | `id` (bigInteger) | None |
| **Product** | `products` | `id` (bigInteger) | `vendor_id -> VendorProfile`, `category_id -> Category` |
| **Order** | `orders` | `id` (bigInteger) | `customer_id -> User` |
| **OrderItem** | `order_items` | `id` (bigInteger) | `order_id -> Order`, `product_id -> Product` |
| **Payment** | `payments` | `id` (bigInteger) | `order_id -> Order`, `user_id -> User` |
| **Review** | `reviews` | `id` (bigInteger) | `product_id -> Product`, `customer_id -> User` |

## Detailed Schema Definitions

### `User` (`users`)

#### Columns

| Column | Type | Nullable | Index / Unique | Constraints & Details |
| :--- | :--- | :--- | :--- | :--- |
| `id` | `bigInteger` | No | - | - |
| `name` | `string` | No | - | - |
| `email` | `string` | No | UNIQUE | PII: Encrypted/Audited |
| `phone` | `string` | No | UNIQUE | PII: Encrypted/Audited |
| `avatar` | `image` | Yes | - | Max: 2048KB, Mimes: image/jpeg, image/png, image/webp |

#### Eloquent Relationships

| Method | Type | Related Model | Foreign Key | Inverse Method |
| :--- | :--- | :--- | :--- | :--- |
| `vendor_profile()` | `hasOne` | `VendorProfile` | `vendor_profile_id` | `user` |
| `orders()` | `hasMany` | `Order` | `orders_id` | `customer` |
| `payments()` | `hasMany` | `Payment` | `payments_id` | `user` |
| `reviews()` | `hasMany` | `Review` | `reviews_id` | `customer` |

### `VendorProfile` (`vendor_profiles`)

#### Columns

| Column | Type | Nullable | Index / Unique | Constraints & Details |
| :--- | :--- | :--- | :--- | :--- |
| `id` | `bigInteger` | No | - | - |
| `user_id` | `bigInteger` | No | UNIQUE, INDEX | FK -> User |
| `shop_name` | `string` | No | - | - |
| `slug` | `string` | No | UNIQUE, INDEX | - |
| `description` | `text` | Yes | - | - |
| `logo` | `image` | Yes | - | Max: 4096KB, Mimes: image/jpeg, image/png, image/webp |
| `commission_rate` | `decimal` | No | - | Decimal(5, 2) |

#### Eloquent Relationships

| Method | Type | Related Model | Foreign Key | Inverse Method |
| :--- | :--- | :--- | :--- | :--- |
| `user()` | `belongsTo` | `User` | `user_id` | `vendor_profile` |
| `products()` | `hasMany` | `Product` | `products_id` | `vendor` |

### `Category` (`categories`)

#### Columns

| Column | Type | Nullable | Index / Unique | Constraints & Details |
| :--- | :--- | :--- | :--- | :--- |
| `id` | `bigInteger` | No | - | - |
| `name` | `string` | No | - | - |
| `slug` | `string` | No | UNIQUE, INDEX | - |
| `description` | `text` | Yes | - | - |

#### Eloquent Relationships

| Method | Type | Related Model | Foreign Key | Inverse Method |
| :--- | :--- | :--- | :--- | :--- |
| `products()` | `hasMany` | `Product` | `products_id` | `category` |

### `Product` (`products`)

#### Columns

| Column | Type | Nullable | Index / Unique | Constraints & Details |
| :--- | :--- | :--- | :--- | :--- |
| `id` | `bigInteger` | No | - | - |
| `vendor_id` | `bigInteger` | No | INDEX | FK -> VendorProfile |
| `category_id` | `bigInteger` | No | INDEX | FK -> Category |
| `title` | `string` | No | - | - |
| `slug` | `string` | No | UNIQUE, INDEX | - |
| `price` | `decimal` | No | - | Decimal(12, 2) |
| `stock` | `integer` | No | - | - |
| `cover_image` | `image` | No | - | Max: 5120KB, Mimes: image/jpeg, image/png, image/webp |
| `status` | `enum` | No | - | Values: [draft, published, archived] |

#### Eloquent Relationships

| Method | Type | Related Model | Foreign Key | Inverse Method |
| :--- | :--- | :--- | :--- | :--- |
| `vendor()` | `belongsTo` | `VendorProfile` | `vendor_id` | `products` |
| `category()` | `belongsTo` | `Category` | `category_id` | `products` |
| `order_items()` | `hasMany` | `OrderItem` | `order_items_id` | `product` |
| `reviews()` | `hasMany` | `Review` | `reviews_id` | `product` |

### `Order` (`orders`)

#### Columns

| Column | Type | Nullable | Index / Unique | Constraints & Details |
| :--- | :--- | :--- | :--- | :--- |
| `id` | `bigInteger` | No | - | - |
| `customer_id` | `bigInteger` | No | INDEX | FK -> User |
| `order_number` | `string` | No | UNIQUE, INDEX | - |
| `subtotal_amount` | `decimal` | No | - | Decimal(12, 2) |
| `tax_amount` | `decimal` | No | - | Decimal(12, 2) |
| `total_amount` | `decimal` | No | - | Decimal(12, 2) |
| `status` | `string` | No | - | - |

#### Eloquent Relationships

| Method | Type | Related Model | Foreign Key | Inverse Method |
| :--- | :--- | :--- | :--- | :--- |
| `customer()` | `belongsTo` | `User` | `customer_id` | `orders` |
| `items()` | `hasMany` | `OrderItem` | `items_id` | `order` |
| `payments()` | `hasMany` | `Payment` | `payments_id` | `order` |

### `OrderItem` (`order_items`)

#### Columns

| Column | Type | Nullable | Index / Unique | Constraints & Details |
| :--- | :--- | :--- | :--- | :--- |
| `id` | `bigInteger` | No | - | - |
| `order_id` | `bigInteger` | No | INDEX | FK -> Order |
| `product_id` | `bigInteger` | No | INDEX | FK -> Product |
| `quantity` | `integer` | No | - | - |
| `unit_price` | `decimal` | No | - | Decimal(12, 2) |
| `subtotal_price` | `decimal` | No | - | Decimal(12, 2) |

#### Eloquent Relationships

| Method | Type | Related Model | Foreign Key | Inverse Method |
| :--- | :--- | :--- | :--- | :--- |
| `order()` | `belongsTo` | `Order` | `order_id` | `items` |
| `product()` | `belongsTo` | `Product` | `product_id` | `order_items` |

### `Payment` (`payments`)

#### Columns

| Column | Type | Nullable | Index / Unique | Constraints & Details |
| :--- | :--- | :--- | :--- | :--- |
| `id` | `bigInteger` | No | - | - |
| `order_id` | `bigInteger` | No | INDEX | FK -> Order |
| `user_id` | `bigInteger` | No | INDEX | FK -> User |
| `gateway` | `string` | No | - | - |
| `amount` | `decimal` | No | - | Decimal(12, 2) |
| `authority` | `string` | No | INDEX | - |
| `ref_id` | `string` | Yes | - | - |
| `tracking_code` | `string` | Yes | - | - |
| `card_pan_masked` | `string` | Yes | - | - |
| `verified_at` | `datetime` | Yes | - | - |
| `failure_reason` | `string` | Yes | - | - |
| `idempotency_key` | `string` | No | UNIQUE, INDEX | - |
| `status` | `string` | No | - | - |

#### Eloquent Relationships

| Method | Type | Related Model | Foreign Key | Inverse Method |
| :--- | :--- | :--- | :--- | :--- |
| `order()` | `belongsTo` | `Order` | `order_id` | `payments` |
| `user()` | `belongsTo` | `User` | `user_id` | `payments` |

### `Review` (`reviews`)

#### Columns

| Column | Type | Nullable | Index / Unique | Constraints & Details |
| :--- | :--- | :--- | :--- | :--- |
| `id` | `bigInteger` | No | - | - |
| `product_id` | `bigInteger` | No | INDEX | FK -> Product |
| `customer_id` | `bigInteger` | No | INDEX | FK -> User |
| `rating` | `integer` | No | - | - |
| `comment` | `text` | No | - | - |

#### Eloquent Relationships

| Method | Type | Related Model | Foreign Key | Inverse Method |
| :--- | :--- | :--- | :--- | :--- |
| `product()` | `belongsTo` | `Product` | `product_id` | `reviews` |
| `customer()` | `belongsTo` | `User` | `customer_id` | `reviews` |
