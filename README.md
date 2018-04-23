# The Quake III Bot Adam
An agent that uses neural network evolved by NEAT, to act as a bot in Quake III. The bots changes neural network depenndin

## Requirements

- Ubuntu 16.04 =<
- Python 3.6
- [Custom Quake III Engine](https://github.com/Botched135/ioq3)
- [Python NEAT](http://neat-python.readthedocs.io/en/latest/installation.html)

In addition, for running the biofeedback controlled agents, you need:

- Empatica E4 Armband
- [Empatica BLE Client](https://github.com/empatica/ble-client-windows)
- [Empatica BLE Server](http://developer.empatica.com/windows-ble-server.html)
- [Bluetooth dongle for connection to E4-server](https://www.silabs.com/products/wireless/bluetooth/bluetooth-low-energy-modules/bled112-bluetooth-smart-dongle)


## Training

To run the training algorithm 

	``` bash
	python3 q3Trainer.py
	```

The default argument(expect path arguments) should work for most. A list of commands can be found through `python3 q3Trainer.py --help`

To run without training, use the command dry run (-d 1). This is useful for debugging the engine.


## Playing

## TO-DO

Later on there will be added C# side to handle the biofeedback, and at some point, other biofeedback devices will be supported.