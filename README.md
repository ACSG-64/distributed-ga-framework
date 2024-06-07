# Distributed GA Framework

> **NOTE**: I originally created this framework for personal use, but I decided to make it open source. As such, the
> codebase is not as _clean_ and _high quality_ as other public projects. Additionally, this repository may not be
> maintained actively.

A simple framework for distributing the workload of evaluating individuals in a horizontally scalable manner.

## Basic schematic
![Distributed GA](https://github.com/ACSG-64/distributed-ga-framework/assets/50815104/53b7e3f5-8458-4b0a-af14-f103acd73f35)

## Getting started
Both the coordinator and the worker have runners that set up the essential working configuration to run each application.
These runners were tested using the built-in implementations of the services, but they should work fine if you use other 
implementations.

To add extensions without the need to edit the source code, many components emit events that your custom listeners can listen to.

### Dependencies
Base dependencies for both components can be found in the `requirements.txt` file.

### Coordinator
At a minimum, you need to create your custom experiment class implementing the `IExperiment` _interface_ 
where its method, `apply_genetic_operations`, will be called by the coordinator when a generation is evaluated, so it 
would be appropriate to apply the genetic operators in that method in order to create a new generation.

After creating the new generation, call `_next`, otherwise, if you want to stop the experimentation, call `_stop`. 
Feel free to check an example of this in the `coordinator/experimenter/experiments/my_experiment.py` file.

If you set a fitness to an individual (`IndividualEntity`), it will be stored in the next generation, but 
it won't be part of the testing sample that is passed to the `testing sample` listeners (those listeners added through the 
coordinator's `add_on_testing_sample_selected_listener` method) since it was already evaluated. You could take
advantage of this behaviour to, for example, apply the `elite` strategy.


_Check the `coordinator/main.py` file for a simple demo on how to set up the components._

### Worker
At a minimum, you need to create your custom evaluator class implementing the `IExperiment` _interface_ 
where its method, `evaluate_sample`, will be called by the local coordinator when a sample is ready to be evaluated.

After evaluating the sample, call `_next`. Feel free to check an example of this in the `worker/experimenter/evaluators/my_evaluator.py` file.

_Check the `worker/main.py` file for a simple demo on how to set up the components._

## Built-in implementations
* **Messaging bus/queues** and **PubSub**: any AMQP 0-9-1 compatible service could be used.
By using this protocol, you could add or remove any number of workers at any time.
* **Persistent storage**: SQLite, both an in-memory and a persistent implementation.

## Contact
* Do you have questions? ask them in the Discussion page
