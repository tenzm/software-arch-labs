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
                description "Регистрация, аутентификация, управление пользователями с кешированием"
                technology "FastAPI, Python, JWT, bcrypt, PostgreSQL, Redis"
                
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
                
                cached_user_repository = component "Cached User Repository" {
                    description "Кеширующий репозиторий с паттернами read-through и write-through"
                    technology "Python, Redis, Write-through, Read-through"
                }
                
                postgres_user_repo = component "PostgreSQL User Repository" {
                    description "Реализация репозитория на PostgreSQL"
                    technology "Python, SQLAlchemy"
                }
                
                redis_client = component "Redis Client" {
                    description "Клиент для работы с Redis кешем"
                    technology "aioredis, JSON serialization"
                }
                
                jwt_service = component "JWT Service" {
                    description "Сервис для работы с JWT токенами"
                    technology "PyJWT"
                }
            }

            catalog_service = container "Catalog Service" {
                description "Управление каталогом услуг"
                technology "FastAPI, Python, MongoDB"
                
                # Компоненты Catalog Service
                catalog_controller = component "Catalog Controller" {
                    description "REST API контроллеры для каталога услуг"
                    technology "FastAPI"
                }
                
                catalog_use_cases = component "Catalog Use Cases" {
                    description "Бизнес-логика управления каталогом"
                    technology "Python"
                }
                
                catalog_domain = component "Catalog Domain" {
                    description "Доменные сущности услуг и категорий"
                    technology "Python, dataclasses"
                }
                
                catalog_repository = component "Catalog Repository" {
                    description "Абстракция доступа к данным каталога"
                    technology "Python, ABC"
                }
                
                mongo_catalog_repo = component "MongoDB Catalog Repository" {
                    description "Реализация репозитория на MongoDB"
                    technology "Python, motor, pymongo"
                }
            }

            order_service = container "Order Service" {
                description "Создание и обработка заказов"
                technology "FastAPI, Python, PostgreSQL"
            }

            group "Слой данных" {
                user_db = container "User DB" {
                    description "БД пользователей"
                    technology "PostgreSQL"
                    tags "database"
                }

                catalog_db = container "Catalog DB" {
                    description "БД услуг и категорий"
                    technology "MongoDB 5.0"
                    tags "database,nosql"
                }

                order_db = container "Order DB" {
                    description "БД заказов"
                    technology "PostgreSQL"
                    tags "database"
                }
                
                redis_cache = container "Redis Cache" {
                    description "Кеш для пользовательских данных с TTL"
                    technology "Redis 7"
                    tags "cache"
                }
            }

            # Связи между контейнерами
            user -> userplane_bff "HTTP/REST API"
            admin -> admin_bff "HTTP/REST API"
            user -> profi_platform "Взаимодействие через платформу"

            userplane_bff -> user_service "HTTP/REST API"
            admin_bff -> user_service "HTTP/REST API"
            user_service -> user_db "Чтение/запись данных о пользователях"
            user_service -> redis_cache "Кеширование пользовательских данных (read-through/write-through)"

            userplane_bff -> catalog_service "HTTP/REST API"
            admin_bff -> catalog_service "HTTP/REST API"
            catalog_service -> catalog_db "Чтение/запись услуг и категорий (CRUD + индексы)"

            userplane_bff -> order_service "HTTP/REST API"
            admin_bff -> order_service "HTTP/REST API"
            order_service -> order_db "Чтение/запись заказов"
            order_service -> user_service "Проверка пользователя"
            order_service -> catalog_service "Проверка услуги при добавлении в заказ"
            
            # Связи внутри User Service
            user_controller -> user_use_cases "Вызов бизнес-логики"
            user_use_cases -> user_domain "Использование доменных сущностей"
            user_use_cases -> user_repository "Доступ к данным"
            user_repository -> cached_user_repository "Кеширующая реализация"
            cached_user_repository -> postgres_user_repo "Делегирование к PostgreSQL репозиторию"
            cached_user_repository -> redis_client "Управление кешем"
            postgres_user_repo -> user_db "PostgreSQL с индексами"
            redis_client -> redis_cache "Операции с Redis кешем"
            user_controller -> jwt_service "Создание/валидация токенов"
            
            # Связи внутри Catalog Service
            catalog_controller -> catalog_use_cases "Вызов бизнес-логики"
            catalog_use_cases -> catalog_domain "Использование доменных сущностей"
            catalog_use_cases -> catalog_repository "Доступ к данным"
            catalog_repository -> mongo_catalog_repo "Реализация"
            mongo_catalog_repo -> catalog_db "MongoDB с индексами и полнотекстовым поиском"
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
                    technology "Docker Container, Port 8080:8000"
                    containerInstance profi_platform.user_service
                }

                deploymentNode "Catalog Service Container" {
                    technology "Docker Container, Port 8081:8001"
                    containerInstance profi_platform.catalog_service
                }

                deploymentNode "Order Service Container" {
                    technology "Docker Container"
                    containerInstance profi_platform.order_service
                }

                deploymentNode "Databases" {
                    deploymentNode "PostgreSQL Container" {
                        technology "PostgreSQL 14, Port 5433:5432"
                        containerInstance profi_platform.user_db
                        containerInstance profi_platform.order_db
                    }

                    deploymentNode "MongoDB Container" {
                        technology "MongoDB 5.0, Port 27017:27017"
                        containerInstance profi_platform.catalog_db
                    }
                    
                    deploymentNode "Redis Container" {
                        technology "Redis 7, Port 6379:6379"
                        containerInstance profi_platform.redis_cache
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

        deployment profi_platform "Production" {
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

        dynamic profi_platform "UC10" "Получение пользователя с кешем (read-through)" {
            autoLayout
            user -> profi_platform.userplane_bff "GET /api/v1/users/{id}"
            profi_platform.userplane_bff -> profi_platform.user_service "Получить пользователя"
            profi_platform.user_service -> profi_platform.redis_cache "Проверка кеша"
            profi_platform.redis_cache -> profi_platform.user_service "Cache miss"
            profi_platform.user_service -> profi_platform.user_db "Загрузка из БД"
            profi_platform.user_service -> profi_platform.redis_cache "Кеширование данных"
            profi_platform.user_service -> profi_platform.userplane_bff "Возврат данных"
        }

        dynamic profi_platform "UC11" "Создание пользователя с кешем (write-through)" {
            autoLayout
            user -> profi_platform.userplane_bff "POST /api/v1/users"
            profi_platform.userplane_bff -> profi_platform.user_service "Создать пользователя"
            profi_platform.user_service -> profi_platform.user_db "Сохранение в БД"
            profi_platform.user_service -> profi_platform.redis_cache "Кеширование созданного пользователя"
            profi_platform.user_service -> profi_platform.userplane_bff "Возврат созданного пользователя"
        }

        theme default

        styles {
            element "Person" {
                color #ffffff
                fontSize 22
                shape Person
            }
            element "Software System" {
                background #1e6091
                color #ffffff
            }
            element "Container" {
                background #2e7bb6
                color #ffffff
            }
            element "Component" {
                background #85BBF0
                color #000000
            }
            element "database" {
                shape Cylinder
                background #8B4513
                color #ffffff
            }
            element "nosql" {
                shape Cylinder
                background #228B22
                color #ffffff
            }
            element "cache" {
                shape Cylinder
                background #FF6B35
                color #ffffff
            }
        }

        properties {
            structurizr.tooltips true
        }
    }
}
