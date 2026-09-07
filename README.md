# IS2-TP-Individual

## Tabla de contenidos

- [Introducción](#introducción)
- [Decisiones de implementación](#decisiones-de-implementación)
- [Arquitectura](#arquitectura)
- [Desafíos Encontrados](#desafíos-encontrados)
- [Posibles Mejoras](#posibles-mejoras)
- [Pre-requisitos](#pre-requisitos)
- [Ejecución](#ejecución)
    - [Variables de entorno](#variables-de-entorno)
    - [Docker](#docker)
    - [Base de Datos](#base-de-datos)
    - [Página HTML](#página-html)
- [Endpoints](#endpoints)

## Introducción

En el presente trabajo se desarrolló un servicio backend de chat mínimo que expone una API REST para administrar canales y consultar el historial de mensajes, junto con un WebSocket por canal que permite a los clientes enviar y editar mensajes, así como recibir en tiempo real los mensajes nuevos y editados. Además, se incluye una página HTML mínima que se conecta al WebSocket y permite visualizar los mensajes recibidos y sus ediciones en tiempo real.  

## Decisiones de implementación

- **Lenguaje Python (v3.12)**: se utilizó como lenguaje principal para el desarrollo del backend.  
- **FastAPI**: se utilizó para implementar la API REST y los endpoints WebSocket.
- **PostgreSQL**: se utilizó como sistema de gestión de base de datos para garantizar la persistencia de canales y mensajes.  
- **Pydantic**: se utilizó para definir los esquemas de entrada y salida.
- **WebSocket**: se implementó un endpoint WebSocket por canal para permitir el envío, edición y recepción de mensajes en tiempo real.  
- **Manejo de errores**: se implementó un middleware para centralizar el manejo de excepciones y devolver respuestas en formato RFC 7807 (`application/problem+json`).  
- **Logging**: se implementó un sistema de logging utilizando la biblioteca externa `loguru` para registrar eventos relevantes de la aplicación y facilitar el monitoreo y diagnóstico de errores.   
- **Docker**: se utilizó Docker y Docker Compose para ejecutar la aplicación y PostgreSQL como servicios independientes.  
- **Variables de entorno**: la configuración de la aplicación y la base de datos se gestiona mediante variables de entorno definidas en un archivo `.env`.  
- **Testing**: se utilizó [`pytest`](https://docs.pytest.org/en/stable/) para implementar y ejecutar pruebas automatizadas de los distintos componentes y funcionalidades del backend.  
- **Página HTML**: se desarrolló una interfaz mínima en la carpeta `/public` para demostrar el funcionamiento del WebSocket y visualizar los mensajes y sus ediciones en tiempo real.  
- **Makefile**: se incorporó para facilitar la ejecución de los principales comandos del proyecto, como iniciar y detener los servicios mediante Docker Compose, así como para correr los tests.  
- **Formateo del código**: se utilizo `ruff` para formatear el código. 
- **Pool de conexiones**: se implementó un pool de conexiones para PostgreSQL, permitiendo reutilizar conexiones a la base de datos y gestionar de manera eficiente múltiples solicitudes concurrentes. 

## Arquitectura

Como estructura de la implementación se decidió seguir una arquitectura en capas, separando las responsabilidades de la API, la lógica de acceso a datos y la persistencia de la siguiente manera:  
- **Api**: contiene los endpoints de la aplicación y se encarga de recibir y procesar las solicitudes HTTP y las conexiones WebSocket.  
- **Services**: contiene la lógica de negocio de la aplicación, actuando como intermediario entre la API y los repositorios.  
- **Repositories**: encapsula las operaciones de acceso a la base de datos, gestionando la persistencia y consulta de canales y mensajes en PostgreSQL.  

## Desafíos Encontrados

Me llevó mucho tiempo aprender y entender cómo realizar una API REST, ya que nunca antes lo había hecho, por lo que tan solo implementar el primer endpoint (siguiendo la arquitectura en capas y buenas prácticas) me llevó varias horas. No entendía qué responsabilidad tenía cada capa, ni tampoco cómo conectar la base de datos. Lograr la conexión e implementar el primer endpoint end to end (con buenas prácticas, utilizando los containers y tests unitarios) fue un gran desafío.  
Los siguientes endpoints los implementé sin mayor problema, pero el siguiente gran desafío fue implementar los tests de integración. En un comienzo utilice el servicio de la base de datos definido en mi `compose.yaml`, pero crear y eliminar datos ahí solo para testear no me parecía lo más seguro y óptimo, por lo que concluí en hacer servicios totalmente aparte que solo levante para los tests, así como utilizar variables de entorno definidas en un archivo aparte (`.env.test`). En particular, para la base de datos utilicé un servicio temporal que se levanta y elimina solo al correr los tests. Estos están definidos en el archivo `compose.test.yaml`.

## Posibles Mejoras

Una posible mejora a la solución es implementar un pipeline de Integración Continua automatizado mediante GitHub Actions.  

## Pre-requisitos

Para levantar el entorno de desarrollo es necesario contar con:

- Docker
- Docker Compose
- Make, para ejecutar los comandos definidos en el Makefile

## Ejecución

### Variables de entorno

Definir las variables de entorno en el archivo `.env` mediante clonar y configurar el archivo de ejemplo:  

```bash
cp .env.example .env
```

### Docker

#### Levantar contenedores

Levantar los contenedores (API y base de datos):

```bash
make up
```

#### Monitoreo

Visualizar los procesos que estan siendo ejecutados:  

```bash
make ps
```

Ver los logs de ejecución:  

```bash
make logs
```

#### Detener contenedores

```bash
make down
```

#### Testing

```bash
make test
```

### Base de Datos

Si se desea correr únicamente la base de datos, primero debemos levantar el container asociado:  

```bash
docker compose up -d --build database
```

Y si se desea ingresar: 

```bash
docker exec -it discordia-chat-db psql -U DATABASE_USER -d DATABASE_NAME
```

Los datos se guardan en un volumen del Docker. En caso de querer eliminarlos, correr:  

```bash
docker volume rm is2-tp-individual_postgres_data
```


### Página HTML

Para abrir la página HTML de demostración del WebSocket y ver los mensajes en vivo, basta con levantar los containers y arrastrar el archivo `/public/index.html` a un navegador.  
También es posible abrir la página ingresando a:

```bash
http://localhost:PORT/public/index.html
```

## Endpoints

Es posible ver y probar los endpoints a través de Swagger en el navegador con la dirección:  

```bash
http://localhost:PORT/docs
```

Estos son: 

```bash
POST /channels
GET /channels
GET /channels/{channelId}/messages
```

Pero en caso de querer publicar mensajes, editarlos, y verlos en tiempo real, se puede utilizar la página HTML. Para ello, se abre en el navegador, se hace click derecho, y en la sección de `Inspeccionar -> Console` es posible utilizar el WebSocket conectado, por ejemplo, para crear mensajes de la siguiente manera:  

```JavaScript
ws.send(JSON.stringify({
    authorId: 1,
    content: "Esto es un mensaje"
}));
```

Y al crearlo podremos verlo publicado en tiempo real, desde el mismo cliente o desde otro, sin recargar la página.  
