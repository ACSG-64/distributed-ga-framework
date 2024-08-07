# Distributed GA Framework

> **NOTE**: I originally created this framework for personal use, but I decided to make it open source. As such, the
> codebase is not as _clean_ and _high quality_ as other public projects. Additionally, this repository may not be
> maintained actively.

A horizontal scaling framework to distribute the evaluation of individuals.

## Basic schematic
![Distributed GA](https://github.com/ACSG-64/distributed-ga-framework/assets/50815104/53b7e3f5-8458-4b0a-af14-f103acd73f35)
*  **Original proposal:** [https://gist.github.com/ACSG-64/e791917544bef41f8cfe56346b831726](https://gist.github.com/ACSG-64/e791917544bef41f8cfe56346b831726)

## Getting started
Both the coordinator and the worker have runners that set up the essential working configuration to run each application.
These runners were tested using the built-in implementations of the services, but they should work fine if you use other 
implementations.

To add extensions without the need to edit the source code, many components emit events that your custom listeners can listen to.

### Dependencies
Base dependencies for both components can be found in the `requirements.txt` file.

The software was tested using Python 3.12 but it should work fine with Python 3.10 and above.

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


_Check the `coordinator/example_main.py` file for a simple example on how to set up the components._

### Worker
At a minimum, you need to create your custom evaluator class implementing the `IExperiment` _interface_ 
where its method, `evaluate_sample`, will be called by the local coordinator when a sample is ready to be evaluated.

After evaluating the sample, call `_next`. Feel free to check an example of this in the `worker/experimenter/evaluators/my_evaluator.py` file.

_Check the `worker/example_main.py` file for a simple example on how to set up the components._

## Built-in implementations
* **Message bus/queues** and **PubSub**: any AMQP 0-9-1 compatible service could be used. By using this protocol, you could add or remove any number of workers at any time.
* **Persistent storage**: SQLite, both an in-memory and a persistent implementation.

## Citation
If you use this software for academic purposes, please add an appropriate citation.

**APA**

`Sarmiento Garzón, A. C. (2024). Distributed GA Framework [Computer software]. https://github.com/ACSG-64/distributed-ga-framework`

**BibTeX**
```
@software{Sarmiento_Garzon_Distributed_GA_Framework_2024,
  author = {Sarmiento Garzón, Andrés Camilo},
  license = {AGPL-3.0},
  month = jun,
  title = {{Distributed GA Framework}},
  url = {https://github.com/ACSG-64/distributed-ga-framework},
  year = {2024}
}

```

## Contact
* Do you have questions? ask them in the Discussion page
