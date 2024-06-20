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
from inventory.views import createInventory, updateInventory, deleteInventory, listInventory,inventoryInfo, transferProduct, cycleCount, createReplenishmentRequest, listReplenishmentRequests, approveReplenishmentRequest, rejectReplenishmentRequest
from shipments.views import createShipment, updateShipment, deleteShipment, listShipments, shipmentInfo, receiveProduct, shipmentDetails
from putaway.views import suggestLocations, browseReceivedProducts, putAwayProduct
from orders.views import deliveryRecordList, createOrder, updateOrder, cancelOrder, viewOrderStatus, getOrderDetails, viewMyOrders, listOrders, prioritizeOrder, updateOrderStatus, getPickList, pickProduct, packOrder, listPackedOrders, assignOrdersToDeliveryMan
from activities.views import listActivities
from wallets.views import listWallets, myTransactionLog, viewWallet, addFunds
from reports.views import listReports, getReportById, generateReport


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
    path('api/products/<str:barcode>/details/', getProductDetailsByBarcode, name='getProductInfo'),
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

    # Shipment management APIs
    path('api/shipments/', listShipments, name='listShipments'),
    path('api/shipments/<int:id>/', shipmentInfo, name='shipmentInfo'),
    path('api/shipments/create/', createShipment, name='createShipment'),
    path('api/shipments/update/<int:id>/', updateShipment, name='updateShipment'),
    path('api/shipments/delete/<int:id>/', deleteShipment, name='deleteShipment'),
    path('api/shipments/receive/<int:shipment_id>/<str:barcode>/', receiveProduct, name='receiveProduct'),
    path('api/shipments/details/<int:shipment_id>/', shipmentDetails, name='shipmentDetails'),

    # Activities management API
    path('api/activities/', listActivities, name='listActivities'),

    # Inventory management APIs
    path('api/inventory/', listInventory, name='listInventory'),
    path('api/inventory/<int:id>/', inventoryInfo, name='inventoryInfo'),
    path('api/inventory/create/', createInventory, name='createInventory'),
    path('api/inventory/update/<int:id>/', updateInventory, name='updateInventory'),
    path('api/inventory/delete/<int:id>/', deleteInventory, name='deleteInventory'),
    path('api/inventory/transfer/', transferProduct, name='transferProduct'),
    path('api/inventory/cycle-count/', cycleCount, name='cycleCount'),
    path('api/inventory/replenishment-request/create/', createReplenishmentRequest, name='createReplenishmentRequest'),
    path('api/inventory/replenishment-requests/', listReplenishmentRequests, name='listReplenishmentRequests'),
    path('api/inventory/replenishment-request/<int:request_id>/approve/', approveReplenishmentRequest, name='approveReplenishmentRequest'),
    path('api/inventory/replenishment-request/<int:request_id>/reject/', rejectReplenishmentRequest, name='rejectReplenishmentRequest'),


    # Put Away APIs
    path('api/shipments/products/received/', browseReceivedProducts, name='receivedProducts'),
    path('api/shipments/details/<int:shipment_detail_id>/suggest-locations/', suggestLocations, name='suggestLocations'),
    path('api/shipments/products/put-away/', putAwayProduct, name='putAwayProduct'),

    # Orders management APIs
    path('api/orders/create/', createOrder, name='createOrder'),
    path('api/orders/update/<int:order_id>/', updateOrder, name='updateOrder'),
    path('api/orders/cancel/<int:order_id>/', cancelOrder, name='cancelOrder'),
    path('api/orders/status/<int:order_id>/', viewOrderStatus, name='viewOrderStatus'),
    path('api/orders/details/<int:order_id>/', getOrderDetails, name='getOrderDetails'),
    path('api/orders/my-orders/', viewMyOrders, name='viewMyOrders'),
    path('api/orders/list-all/', listOrders, name='listOrders'),
    path('api/orders/prioritize/<int:order_id>/', prioritizeOrder, name='prioritizeOrder'),
    path('api/orders/update-status/<int:order_id>/', updateOrderStatus, name='updateOrderStatus'),
    path('api/orders/pick-list/<int:order_detail_id>/', getPickList, name='getPickList'),
    path('api/orders/pick/<int:order_detail_id>/<str:location_barcode>/', pickProduct, name='pickProduct'),
    path('api/orders/pack/<int:order_id>/', packOrder, name='packOrder'),
    path('api/orders/packed/', listPackedOrders, name='listPackedOrders'),
    path('api/orders/assign-delivery-man/', assignOrdersToDeliveryMan, name='assignOrdersToDeliveryMan'),
    path('api/orders/delivery-records/', deliveryRecordList, name='deliveryRecordList'),

    # Wallets management API
    path('api/wallets/my-wallet/', viewWallet, name='viewWallet'),
    path('api/wallets/', listWallets, name='listWallets'),
    path('api/wallets/add-funds/', addFunds, name='addFunds'),
    path('api/wallets/my-transactions/', myTransactionLog, name='myTransactions'),

    # Reports APIs
    path('api/reports/', listReports, name='listReports'),
    path('api/reports/<int:report_id>/', getReportById, name='getReportById'),
    path('api/reports/generate/', generateReport, name='generateReport'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
