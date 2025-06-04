workspace {
    name "Платформа услуг (Profi.ru)"
    description "Описание архитектуры платформы поиска и заказа услуг в стиле Architecture as Code"

    !identifiers hierarchical

    model {
        properties {
            structurizr.groupSeparator "/"
        }

        user = person "Пользователь"
        admin = person "Администратор"

        profi_platform = softwareSystem "Profi.ru" {
            description "Сервис для поиска специалистов и заказа услуг"

            userplane_bff = container "Userplane BFF" {
                description "Промежуточный слой между клиентом (веб/мобайл) и сервисами для пользователей"
            }

            admin_bff = container "Admin BFF" {
                description "Промежуточный слой между админ-интерфейсом и сервисами"
            }

            user_service = container "User Service" {
                description "Регистрация, поиск пользователей"
            }

            catalog_service = container "Catalog Service" {
                description "Управление услугами"
            }

            order_service = container "Order Service" {
                description "Создание и обработка заказов"
            }

            group "Слой данных" {
                user_db = container "User DB" {
                    description "БД пользователей"
                    technology "PostgreSQL"
                    tags "database"
                }

                catalog_db = container "Catalog DB" {
                    description "БД услуг"
                    technology "PostgreSQL"
                    tags "database"
                }

                order_db = container "Order DB" {
                    description "БД заказов"
                    technology "PostgreSQL"
                    tags "database"
                }
            }

            user -> userplane_bff "Доступ пользователя"
            admin -> admin_bff "Доступ администратора"
            user -> profi_platform "Взаимодействие через платформу"

            userplane_bff -> user_service "Работа с пользователями"
            admin_bff -> user_service "Работа с пользователями"
            user_service -> user_db "Чтение/запись данных о пользователях"

            userplane_bff -> catalog_service "Работа с услугами"
            admin_bff -> catalog_service "Работа с услугами"
            catalog_service -> catalog_db "Чтение/запись услуг"

            userplane_bff -> order_service "Работа с заказами"
            admin_bff -> order_service "Просмотр заказов пользователей"
            order_service -> order_db "Чтение/запись заказов"
            order_service -> user_service "Проверка пользователя"
            order_service -> catalog_service "Проверка услуги при добавлении в заказ"
        }

        production = deploymentEnvironment "Production" {
            deploymentNode "BFF Layer" {
                deploymentNode "Userplane BFF Node" {
                    containerInstance profi_platform.userplane_bff
                }
                deploymentNode "Admin BFF Node" {
                    containerInstance profi_platform.admin_bff
                }
            }

            deploymentNode "User Service Node" {
                containerInstance profi_platform.user_service
            }

            deploymentNode "Catalog Service Node" {
                containerInstance profi_platform.catalog_service
            }

            deploymentNode "Order Service Node" {
                containerInstance profi_platform.order_service
            }

            deploymentNode "Databases" {
                deploymentNode "User DB Node" {
                    containerInstance profi_platform.user_db
                }

                deploymentNode "Catalog DB Node" {
                    containerInstance profi_platform.catalog_db
                }

                deploymentNode "Order DB Node" {
                    containerInstance profi_platform.order_db
                }
            }
        }
    }

    views {
        systemContext profi_platform {
            include *
            autoLayout
        }

        container profi_platform {
            include *
            autoLayout
        }

        deployment profi_platform production {
            include *
            autoLayout
        }

        dynamic profi_platform "UC01" "Создание нового пользователя" {
            autoLayout
            user -> profi_platform.userplane_bff "POST /users"
            profi_platform.userplane_bff -> profi_platform.user_service "Создать пользователя"
            profi_platform.user_service -> profi_platform.user_db "Сохраняет пользователя"
        }

        dynamic profi_platform "UC02" "Поиск пользователя по логину" {
            autoLayout
            user -> profi_platform.userplane_bff "GET /users/{login}"
            profi_platform.userplane_bff -> profi_platform.user_service "Поиск пользователя"
            profi_platform.user_service -> profi_platform.user_db "Получает данные"
        }

        dynamic profi_platform "UC03" "Создание заказа" {
            autoLayout
            user -> profi_platform.userplane_bff "POST /orders"
            profi_platform.userplane_bff -> profi_platform.order_service "Создать заказ"
            profi_platform.order_service -> profi_platform.order_db "Сохраняет заказ"
            profi_platform.order_service -> profi_platform.user_service "Проверка пользователя"
        }

        dynamic profi_platform "UC04" "Добавление услуги в заказ" {
            autoLayout
            user -> profi_platform.userplane_bff "POST /orders/{id}/services"
            profi_platform.userplane_bff -> profi_platform.order_service "Добавить услугу в заказ"
            profi_platform.order_service -> profi_platform.catalog_service "Проверка услуги"
            profi_platform.catalog_service -> profi_platform.catalog_db "Получение услуги"
        }

        dynamic profi_platform "UC05" "Просмотр заказов пользователя (админ)" {
            autoLayout
            admin -> profi_platform.admin_bff "GET /orders?user={id}"
            profi_platform.admin_bff -> profi_platform.order_service "Получить список заказов пользователя"
            profi_platform.order_service -> profi_platform.order_db "Чтение заказов по пользователю"
        }

        dynamic profi_platform "UC06" "Редактирование услуги (админ)" {
            autoLayout
            admin -> profi_platform.admin_bff "PUT /services/{id}"
            profi_platform.admin_bff -> profi_platform.catalog_service "Обновить услугу"
            profi_platform.catalog_service -> profi_platform.catalog_db "Изменение данных услуги"
        }

        dynamic profi_platform "UC07" "Поиск пользователя по имени (админ)" {
            autoLayout
            admin -> profi_platform.admin_bff "GET /users?name=..."
            profi_platform.admin_bff -> profi_platform.user_service "Поиск пользователя по имени"
            profi_platform.user_service -> profi_platform.user_db "Фильтрация пользователей по имени"
        }

        theme default

        styles {
            element "database" {
                shape cylinder
            }
        }

        properties {
            structurizr.tooltips true
        }
    }
}
