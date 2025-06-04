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
                technology "FastAPI, Python"
            }

            admin_bff = container "Admin BFF" {
                description "Промежуточный слой между админ-интерфейсом и сервисами"
                technology "FastAPI, Python"
            }

            user_service = container "User Service" {
                description "Регистрация, аутентификация, управление пользователями"
                technology "FastAPI, Python, JWT, bcrypt"
                
                # Компоненты User Service
                user_controller = component "User Controller" {
                    description "REST API контроллеры для управления пользователями"
                    technology "FastAPI"
                }
                
                user_use_cases = component "User Use Cases" {
                    description "Бизнес-логика управления пользователями"
                    technology "Python"
                }
                
                user_domain = component "User Domain" {
                    description "Доменные сущности и правила"
                    technology "Python, dataclasses"
                }
                
                user_repository = component "User Repository" {
                    description "Абстракция доступа к данным пользователей"
                    technology "Python, ABC"
                }
                
                memory_user_repo = component "In-Memory User Repository" {
                    description "Реализация репозитория в памяти"
                    technology "Python, Dict"
                }
                
                jwt_service = component "JWT Service" {
                    description "Сервис для работы с JWT токенами"
                    technology "PyJWT"
                }
            }

            catalog_service = container "Catalog Service" {
                description "Управление каталогом услуг"
                technology "FastAPI, Python"
                
                # Компоненты Catalog Service
                catalog_controller = component "Catalog Controller" {
                    description "REST API контроллеры для каталога услуг"
                    technology "FastAPI"
                }
                
                catalog_domain = component "Catalog Domain" {
                    description "Доменные сущности услуг и категорий"
                    technology "Python, dataclasses"
                }
            }

            order_service = container "Order Service" {
                description "Создание и обработка заказов"
                technology "FastAPI, Python"
            }

            group "Слой данных" {
                user_db = container "User DB" {
                    description "БД пользователей (пока в памяти)"
                    technology "In-Memory Storage"
                    tags "database"
                }

                catalog_db = container "Catalog DB" {
                    description "БД услуг (пока в памяти)"
                    technology "In-Memory Storage"
                    tags "database"
                }

                order_db = container "Order DB" {
                    description "БД заказов"
                    technology "PostgreSQL"
                    tags "database"
                }
            }

            # Связи между контейнерами
            user -> userplane_bff "HTTP/REST API"
            admin -> admin_bff "HTTP/REST API"
            user -> profi_platform "Взаимодействие через платформу"

            userplane_bff -> user_service "HTTP/REST API"
            admin_bff -> user_service "HTTP/REST API"
            user_service -> user_db "Чтение/запись данных о пользователях"

            userplane_bff -> catalog_service "HTTP/REST API"
            admin_bff -> catalog_service "HTTP/REST API"
            catalog_service -> catalog_db "Чтение/запись услуг"

            userplane_bff -> order_service "HTTP/REST API"
            admin_bff -> order_service "HTTP/REST API"
            order_service -> order_db "Чтение/запись заказов"
            order_service -> user_service "Проверка пользователя"
            order_service -> catalog_service "Проверка услуги при добавлении в заказ"
            
            # Связи внутри User Service
            user_controller -> user_use_cases "Вызов бизнес-логики"
            user_use_cases -> user_domain "Использование доменных сущностей"
            user_use_cases -> user_repository "Доступ к данным"
            user_repository -> memory_user_repo "Реализация"
            memory_user_repo -> user_db "Хранение в памяти"
            user_controller -> jwt_service "Создание/валидация токенов"
            
            # Связи внутри Catalog Service
            catalog_controller -> catalog_domain "Использование доменных сущностей"
        }

        production = deploymentEnvironment "Production" {
            deploymentNode "Docker Host" {
                technology "Docker, docker-compose"
                
                deploymentNode "BFF Layer" {
                    deploymentNode "Userplane BFF Container" {
                        technology "Docker Container"
                        containerInstance profi_platform.userplane_bff
                    }
                    deploymentNode "Admin BFF Container" {
                        technology "Docker Container"
                        containerInstance profi_platform.admin_bff
                    }
                }

                deploymentNode "User Service Container" {
                    technology "Docker Container, Port 8000"
                    containerInstance profi_platform.user_service
                }

                deploymentNode "Catalog Service Container" {
                    technology "Docker Container, Port 8001"
                    containerInstance profi_platform.catalog_service
                }

                deploymentNode "Order Service Container" {
                    technology "Docker Container"
                    containerInstance profi_platform.order_service
                }

                deploymentNode "Databases" {
                    deploymentNode "User DB Container" {
                        technology "In-Memory (будет PostgreSQL)"
                        containerInstance profi_platform.user_db
                    }

                    deploymentNode "Catalog DB Container" {
                        technology "In-Memory (будет PostgreSQL)"
                        containerInstance profi_platform.catalog_db
                    }

                    deploymentNode "Order DB Container" {
                        technology "PostgreSQL Container"
                        containerInstance profi_platform.order_db
                    }
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
        
        component profi_platform.user_service {
            include *
            autoLayout
        }
        
        component profi_platform.catalog_service {
            include *
            autoLayout
        }

        deployment profi_platform production {
            include *
            autoLayout
        }

        dynamic profi_platform "UC01" "Создание нового пользователя" {
            autoLayout
            user -> profi_platform.userplane_bff "POST /api/v1/users"
            profi_platform.userplane_bff -> profi_platform.user_service "Создать пользователя"
            profi_platform.user_service -> profi_platform.user_db "Сохраняет пользователя"
        }

        dynamic profi_platform "UC02" "Аутентификация пользователя" {
            autoLayout
            user -> profi_platform.userplane_bff "POST /api/v1/auth/login"
            profi_platform.userplane_bff -> profi_platform.user_service "Аутентификация"
            profi_platform.user_service -> profi_platform.user_db "Проверка учетных данных"
            profi_platform.user_service -> profi_platform.userplane_bff "JWT токен"
            profi_platform.userplane_bff -> user "Токен доступа"
        }

        dynamic profi_platform "UC03" "Поиск пользователя по логину" {
            autoLayout
            user -> profi_platform.userplane_bff "GET /api/v1/users/{login}"
            profi_platform.userplane_bff -> profi_platform.user_service "Поиск пользователя"
            profi_platform.user_service -> profi_platform.user_db "Получает данные"
        }

        dynamic profi_platform "UC04" "Получение списка услуг" {
            autoLayout
            user -> profi_platform.userplane_bff "GET /api/v1/services"
            profi_platform.userplane_bff -> profi_platform.catalog_service "Получить услуги"
            profi_platform.catalog_service -> profi_platform.catalog_db "Чтение услуг"
        }

        dynamic profi_platform "UC05" "Создание заказа" {
            autoLayout
            user -> profi_platform.userplane_bff "POST /orders"
            profi_platform.userplane_bff -> profi_platform.order_service "Создать заказ"
            profi_platform.order_service -> profi_platform.order_db "Сохраняет заказ"
            profi_platform.order_service -> profi_platform.user_service "Проверка пользователя"
        }

        dynamic profi_platform "UC06" "Добавление услуги в заказ" {
            autoLayout
            user -> profi_platform.userplane_bff "POST /orders/{id}/services"
            profi_platform.userplane_bff -> profi_platform.order_service "Добавить услугу в заказ"
            profi_platform.order_service -> profi_platform.catalog_service "Проверка услуги"
            profi_platform.catalog_service -> profi_platform.catalog_db "Получение услуги"
        }

        dynamic profi_platform "UC07" "Просмотр заказов пользователя (админ)" {
            autoLayout
            admin -> profi_platform.admin_bff "GET /orders?user={id}"
            profi_platform.admin_bff -> profi_platform.order_service "Получить список заказов пользователя"
            profi_platform.order_service -> profi_platform.order_db "Чтение заказов по пользователю"
        }

        dynamic profi_platform "UC08" "Редактирование услуги (админ)" {
            autoLayout
            admin -> profi_platform.admin_bff "PUT /services/{id}"
            profi_platform.admin_bff -> profi_platform.catalog_service "Обновить услугу"
            profi_platform.catalog_service -> profi_platform.catalog_db "Изменение данных услуги"
        }

        dynamic profi_platform "UC09" "Поиск пользователя по имени (админ)" {
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
