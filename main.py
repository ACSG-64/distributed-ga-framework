if __name__ == '__main__':
    print('[[DISTRIBUTED GA FRAMEWORK]]')
    print('Which one do you want to run?')
    print('- 1. Coordinator')
    print('- 2. Worker')
    print('- 3. Exit')
    while True:
        selection = input('> Input 1, 2 or 3: ').strip()
        if selection in {'1', '2', '3'}:
            selection = int(selection)
            break
        print(f'Invalid option "{selection}"')
    if selection == 1:
        from coordinator.main import main as coordinator_main

        coordinator_main()
    elif selection == 2:
        from worker.main import main as worker_main

        worker_main()
    else:
        print('Exiting the program...')
