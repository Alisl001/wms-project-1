from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter
from users.views import userRegistration, userAuthTokenLogin, userLogout, passwordResetRequest, passwordResetCodeCheck, passwordResetConfirm, retrieveUserById, myDetails, changeMyPassword, updateUserInfo, disableMyAccount, disableUserById, listStaffMembers, listNewStaffMembers, listCustomers, registerStaffByAdmin
from warehouses.views import createWarehouse, updateWarehouse, deleteWarehouse, listWarehouses
from locations.views import createLocation, updateLocation, deleteLocation, listLocations, locationInfo
from suppliers.views import listSuppliers, supplierInfo, createSupplier, updateSupplier, deleteSupplier, uploadSupplierPhoto
from categories.views import listCategories, categoryInfo, createCategory, updateCategory, deleteCategory, uploadCategoryPhoto
from products.views import createProduct, updateProduct, deleteProduct, getProductInfo, listProducts, listProductsByCategory, listProductsBySupplier, productSearch, uploadProductPhoto, getProductDetailsByBarcode, productSuggestions
from favorites.views import createFavorite, deleteFavorite, myFavorites, topFavoriteProducts, productFavoritedByUsers, userFavoriteCount




urlpatterns = [
    path('admin/', admin.site.urls),

    # User Management APIs
    path('api/register/', userRegistration, name='userRegister'),
    path('api/admin/register-staff/', registerStaffByAdmin, name='registerStaffByAdmin'),
    path('api/login/', userAuthTokenLogin, name='userAuthTokenLogin'),
    path('api/logout/', userLogout, name='userLogout'),
    path('api/password-reset/request/', passwordResetRequest, name='passwordResetRequest'),
    path('api/password-reset/code-check/', passwordResetCodeCheck, name='passwordResetCodeCheck'),
    path('api/password-reset/confirm/', passwordResetConfirm, name='passwordResetConfirm'),
    path('api/users/<int:id>/', retrieveUserById, name='userDetail'),
    path('api/users/my-details/', myDetails, name='myDetails'),
    path('api/user/change-password/', changeMyPassword, name='changePassword'),
    path('api/user/update-info/', updateUserInfo, name='updateUserInfo'),
    path('api/user/disable-my-account/', disableMyAccount, name='disableMyAccount'),
    path('api/users/disable/<int:id>/', disableUserById, name='disableUserAccount'),
    path('api/users/staff/', listStaffMembers, name='listStaffMembers'),
    path('api/users/new-staff-members/', listNewStaffMembers, name='listNewStaffMembers'),
    path('api/users/customers/', listCustomers, name='listCustomers'),

    # Warehouse CRUD APIs
    path('api/warehouse/create/', createWarehouse, name='createWarehouse'),
    path('api/warehouse/update/<int:id>/', updateWarehouse, name='updateWarehouse'),
    path('api/warehouse/delete/<int:id>/', deleteWarehouse, name='deleteWarehouse'),
    path('api/warehouses/', listWarehouses, name='listWarehouses'),

    # Locations CRUD APIs
    path('api/locations/', listLocations, name='listLocations'),
    path('api/locations/<int:id>/', locationInfo, name='locationInfo'),
    path('api/locations/create/', createLocation, name='createLocation'),
    path('api/locations/update/<int:id>/', updateLocation, name='updateLocation'),
    path('api/locations/delete/<int:id>/', deleteLocation, name='deleteLocation'),

    # Suppliers management APIs
    path('api/suppliers/', listSuppliers, name='listSuppliers'),
    path('api/suppliers/<int:id>/', supplierInfo, name='supplierInfo'),
    path('api/suppliers/create/', createSupplier, name='createSupplier'),
    path('api/suppliers/<int:id>/update/', updateSupplier, name='updateSupplier'),
    path('api/suppliers/<int:id>/delete/', deleteSupplier, name='deleteSupplier'),
    path('api/suppliers/<int:id>/upload-photo/', uploadSupplierPhoto, name='uploadSupplierPhoto'),

    # Categories management APIs
    path('api/categories/', listCategories, name='listCategories'),
    path('api/categories/<int:id>/', categoryInfo, name='categoryInfo'),
    path('api/categories/create/', createCategory, name='createCategory'),
    path('api/categories/<int:id>/update/', updateCategory, name='updateCategory'),
    path('api/categories/<int:id>/delete/', deleteCategory, name='deleteCategory'),
    path('api/categories/<int:id>/upload-photo/', uploadCategoryPhoto, name='uploadCategoryPhoto'),

    #Products management APIs
    path('api/products/create/', createProduct, name='createProduct'),
    path('api/products/<int:id>/update/', updateProduct, name='updateProduct'),
    path('api/products/<int:id>/delete/', deleteProduct, name='deleteProduct'),
    path('api/products/<int:id>/', getProductInfo, name='getProductInfo'),
    path('api/products/details/barcode/', getProductDetailsByBarcode, name='getProductInfo'),
    path('api/products/', listProducts, name='listProducts'),
    path('api/products/category/<int:category_id>/', listProductsByCategory, name='listProductsByCategory'),
    path('api/products/supplier/<int:supplier_id>/', listProductsBySupplier, name='listProductsBySupplier'),
    path('api/products/<int:id>/upload-photo/', uploadProductPhoto, name='uploadProductPhoto'),
    path('api/products/search/', productSearch, name='productSearch'),
    path('api/products/suggestions/', productSuggestions, name='productSuggestions'),

    # Favorite management APIs
    path('api/products/<int:product_id>/favorites/create/', createFavorite, name='createFavorite'),
    path('api/products/<int:product_id>/favorites/delete/', deleteFavorite, name='deleteFavorite'),
    path('api/products/<int:product_id>/favorites/count/', productFavoritedByUsers, name='productFavoritedByUsers'),
    path('api/products/my-favorites/', myFavorites, name='myFavorites'),
    path('api/products/top-10-favorite/', topFavoriteProducts, name='topFavoriteProducts'),
    path('api/users/<int:user_id>/favorites-count/', userFavoriteCount, name='userFavoriteCount'),


] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
