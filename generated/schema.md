# Database Schema

## Table: Album

| Column | Type | PK | FK |
|--------|------|----|----|
| AlbumId | INTEGER | ✓ |  |
| Title | NVARCHAR(160) |  |  |
| ArtistId | INTEGER |  | → Artist.ArtistId |

## Table: Artist

| Column | Type | PK | FK |
|--------|------|----|----|
| ArtistId | INTEGER | ✓ |  |
| Name | NVARCHAR(120) |  |  |

## Table: Customer

| Column | Type | PK | FK |
|--------|------|----|----|
| CustomerId | INTEGER | ✓ |  |
| FirstName | NVARCHAR(40) |  |  |
| LastName | NVARCHAR(20) |  |  |
| Company | NVARCHAR(80) |  |  |
| Address | NVARCHAR(70) |  |  |
| City | NVARCHAR(40) |  |  |
| State | NVARCHAR(40) |  |  |
| Country | NVARCHAR(40) |  |  |
| PostalCode | NVARCHAR(10) |  |  |
| Phone | NVARCHAR(24) |  |  |
| Fax | NVARCHAR(24) |  |  |
| Email | NVARCHAR(60) |  |  |
| SupportRepId | INTEGER |  | → Employee.EmployeeId |

## Table: Employee

| Column | Type | PK | FK |
|--------|------|----|----|
| EmployeeId | INTEGER | ✓ |  |
| LastName | NVARCHAR(20) |  |  |
| FirstName | NVARCHAR(20) |  |  |
| Title | NVARCHAR(30) |  |  |
| ReportsTo | INTEGER |  | → Employee.EmployeeId |
| BirthDate | DATETIME |  |  |
| HireDate | DATETIME |  |  |
| Address | NVARCHAR(70) |  |  |
| City | NVARCHAR(40) |  |  |
| State | NVARCHAR(40) |  |  |
| Country | NVARCHAR(40) |  |  |
| PostalCode | NVARCHAR(10) |  |  |
| Phone | NVARCHAR(24) |  |  |
| Fax | NVARCHAR(24) |  |  |
| Email | NVARCHAR(60) |  |  |

## Table: Genre

| Column | Type | PK | FK |
|--------|------|----|----|
| GenreId | INTEGER | ✓ |  |
| Name | NVARCHAR(120) |  |  |

## Table: Invoice

| Column | Type | PK | FK |
|--------|------|----|----|
| InvoiceId | INTEGER | ✓ |  |
| CustomerId | INTEGER |  | → Customer.CustomerId |
| InvoiceDate | DATETIME |  |  |
| BillingAddress | NVARCHAR(70) |  |  |
| BillingCity | NVARCHAR(40) |  |  |
| BillingState | NVARCHAR(40) |  |  |
| BillingCountry | NVARCHAR(40) |  |  |
| BillingPostalCode | NVARCHAR(10) |  |  |
| Total | NUMERIC(10,2) |  |  |

## Table: InvoiceLine

| Column | Type | PK | FK |
|--------|------|----|----|
| InvoiceLineId | INTEGER | ✓ |  |
| InvoiceId | INTEGER |  | → Invoice.InvoiceId |
| TrackId | INTEGER |  | → Track.TrackId |
| UnitPrice | NUMERIC(10,2) |  |  |
| Quantity | INTEGER |  |  |

## Table: MediaType

| Column | Type | PK | FK |
|--------|------|----|----|
| MediaTypeId | INTEGER | ✓ |  |
| Name | NVARCHAR(120) |  |  |

## Table: Playlist

| Column | Type | PK | FK |
|--------|------|----|----|
| PlaylistId | INTEGER | ✓ |  |
| Name | NVARCHAR(120) |  |  |

## Table: PlaylistTrack

| Column | Type | PK | FK |
|--------|------|----|----|
| PlaylistId | INTEGER | ✓ | → Playlist.PlaylistId |
| TrackId | INTEGER | ✓ | → Track.TrackId |

## Table: Track

| Column | Type | PK | FK |
|--------|------|----|----|
| TrackId | INTEGER | ✓ |  |
| Name | NVARCHAR(200) |  |  |
| AlbumId | INTEGER |  | → Album.AlbumId |
| MediaTypeId | INTEGER |  | → MediaType.MediaTypeId |
| GenreId | INTEGER |  | → Genre.GenreId |
| Composer | NVARCHAR(220) |  |  |
| Milliseconds | INTEGER |  |  |
| Bytes | INTEGER |  |  |
| UnitPrice | NUMERIC(10,2) |  |  |
