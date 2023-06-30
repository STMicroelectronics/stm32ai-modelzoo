/**
 * \page sm_page Sensor Manager
 *
 * \tableofcontents
 *
 * \section intro_sm Introduction
 * SensorManager is an eLooM-based application-level module that interfaces sensors and offers their data to other application modules.
 * It is implemented as an acquisition engine that:
 * - orchestrates multiple task accesses to sensor bus
 * - defines interfaces to avoid implementation dependencies
 * - dispatches events to notify when a certain amount of data is available 
 
 * \section design_sm Design
 * As for any eLooM-based module, the SensorManager is packed into a folder. It is totally self-contained, so it is independent from other modules and 
 * it can be added to your custom FW application by just dragging and dropping the needed folder.
 * Since modules are eLooM based application, the folder structure stands on eLooM layered architecture. Each FW modules implements concretely or extends
 * services, classes and objects made available by the eLooM framework. More specifically, here you can find:
 * -  Drivers, objects that implements the base interface for any low-level subsystem that can be used into the FW module (i.e.: I2C, DFSDM).
 * -  Events, objects that handle information about something that happened in the system at a given moment. These files implement the event and 
 * source/listener design patterns.
 * -  Services, any kind of further utilities for the FW module.
 *
 * Into the root folder of the FW module, there are the application objects, where the features are implemented. These files are always built on top of
 * eLooM interfaces, so that they can be OS-based tasks, managed tasks, drivers or IOdrivers. 

 * \section folder_sm Folder structure
 * The SensorManager folder contains the following kind of files:
 * - Communication: managed tasks and interfaces that implements the bus peripheral communication. The supported peripherals are:
 *   + I2C 
 *   + SPI
 * - Sensors: managed tasks and interfaces that implements the single sensor threads. The supported sensors are:
 *   + HTS221
 *   + IIS3DWB
 *   + IMP23ABSU
 *   + ISM330DHCX
 *   + LPS22HH
 * - Utilities: SensorManager and eLooM macros, services and utilities 
 *
 * \anchor fig1 \image html SensorManager_folder.jpg "Fig.1 - SensorManager files" width=300px

 * \section layer_sm 3-layer architecture
 * SensorManager module is based on a three-layer architecture. There is the Application Layer, where we can find all the SM Tasks. 
 *
 * \ref fig2 "Fig.2" displays an example with the ISM330DHCX Task, in charge to manage the related sensor. 
 *
 * \anchor fig2 \image html eLooM_3_layer.png "Fig.2 - eLooM 3-level structure"
 *
 * The SPIBusTask in charge to schedule and process the SPI request comes from all the sensor tasks.
 * Under the Application layer we find the Service Layer, this layer is like a bridge between the tasks and the low level api typically. 
 * In this case we find the PID (Platform Independent Driver) of the component, that implements the protocol used to communicate with the component itself.
 * Last layer is the Low-Level API, in this layer there are the objects in charge to communicate with the component through a peripheral. In the Low-Level 
 * API the SM application takes advantage of the configuration file generated from CubeMX.
 *
 * Resuming the entire process:
 * - SPIBusTask schedules the requests and processes them via the SPIMasterDriver
 * - The SensorTask implements its own SPIBusIF
 * - The SPIBusIF is used by SPIBusTask
 * - One change to one layer doesn’t affect the other layers.
 * 
 * Note that the Connector  is the same type of the stmdev_ctx_t used in the ST PID sensor driver. 
 * This allows us to reuse that driver (in the eLooM framework the PID is not a driver, but a service, while the low-level API is the I2C/SPI master driver)
 * to control the sensor.
 *
 * \section dataflow_sm Sensor Data flow
 * On top of the PID driver already provided bt ST, SensorManager provides a set of interfaces and abstract classes as displayed in the following Figure. 
 *
 * \ref fig3 "Fig.3" displays how bus interfaces are implemented in the SensorManager.
 *
 * \anchor fig3 \image html bus.png "Fig.3 - Bus Interface UML"
 *
 * \subsection eventlistener_sm Event/Listener design pattern
 * This architecture allows a Managed task, like the SPIBusTask, to export an easy-to-use API to connect and disconnect sensor objects at application level. 
 * The following code shows how to allocate a Sensor (IIS3DWB) and a Bus (SPI3) and how to connect them so that the application knows that a specific sensor 
 * can be accessed through a specific bus.
 *
 *
 *        // Allocate the Tasks objects
 *       sSPI3BusObj = SPIBusTaskAlloc(&MX_SPI3InitParams);
 *       sIIS3DWBObj = IIS3DWBTaskAlloc();
 *         
 *       // Add Tasks to the Application Context
 *       res = ACAddTask(pAppContext, (AManagedTask*)sSPI3BusObj);
 *       res = ACAddTask(pAppContext, (AManagedTask*)sIIS3DWBObj);
 *       
 *       // Connect the Sensor task to the Bus
 *       SPIBusTaskConnectDevice((SPIBusTask*)sSPI3BusObj, IIS3DWBTaskGetSensorIF((IIS3DWBTask*)sIIS3DWBObj));
 *
 * 
 * Each sensor is handled by a dedicated task at application level to manage data acquisition from the specific sensor.
 * When a read/write transaction is necessary, the task appends a message to the specific bus message queue and waits for an OS semaphore to be released.
 * At this point, since the bus message queue is no longer empty, the bus task wakes up and initiates the actual transaction (read/write) on the bus using 
 * DMA and it enters in a blocked state waiting for the transaction to be completed. In this scenario, data acquisition is handled by the hardware (BUS + DMA)
 * without any intervention of the core. 
 * When the data transaction is completed, the DMA throws an interrupt that wakes up the bus task, which in turn wakes up the task which originally made 
 * the request.
 *
 * \subsection interface_sm Interfaces
 * Each sensor tasks must implement the interfaces required from the SensorManager. 
 * The interfaces abstract a common behavior, so to obtain:
 * - Interface segregation principle (many client-specific interfaces are better than one general-purpose interface).
 * - Easy to extend. You are free to add a new sensor to the Sensor Manager by just implementing the required interfaces.
 * - A barrier preventing coupling to dependencies.
 *
 * \anchor fig4 \image html interfaces.png "Fig.4 - Interfaces implemented in SensorManager"
 * 
 * We have two kinds of interfaces involved:
 * - The ISourceObservable interface is dedicated for which wants just to be an observer of the sensor tasks, which is interested to read information from 
 * the sensor. Basically, the interfaces exposes the Event Source interface of the sensor to the observer.
 * - The ISensor extends the first one adding more features, in this case allow the user Task to control the sensor.
 * 
 */
