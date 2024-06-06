# Distributed GA Framework

> **NOTE**: I originally created this framework for personal use, but I decided to make it open source. As such, the
> codebase is not as _clean_ and _high quality_ as other public projects. Additionally, this repository may not be
> maintained actively.

A simple framework for distributing the workload of evaluating individuals in a horizontally scalable manner.

## Basic schematic
![Distributed GA](https://github.com/ACSG-64/distributed-ga-framework/assets/50815104/53b7e3f5-8458-4b0a-af14-f103acd73f35)

## Built-in implementations
* **Messaging bus/queues** and **PubSub**: any AMQP 0-9-1 compatible service could be used.
By using this protocol, you could add or remove any number of workers at any time.
* **Persistent storage**: SQLite, both an in-memory and a persistent implementation.

## Contact
* Do you have questions? ask them in the Discussion page
