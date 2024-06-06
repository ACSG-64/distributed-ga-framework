# Distributed GA Framework

> **NOTE**: I originally created this framework for personal use, but I decided to make it open source. As such, the
> codebase is not as _clean_ and _high quality_ as other public projects. Additionally, this repository may not be
> maintained actively.

A simple framework to distribute GA workload in a horizontal-scaled manner.

## Basic schematic
![Distributed GA](https://gist.github.com/assets/50815104/0535a622-1617-45ee-998b-2e54cc9739a0)

## Built-in implementations
* **Messaging bus/queues** and **PubSub**: any AMQP 0-9-1 compatible service could be used.
By using this protocol, you could add or remove any number of workers at any time.
* **Persistent storage**: SQLite, both an in-memory and a persistent implementation.

## Contact
* Do you have questions? ask them in the Discussion page