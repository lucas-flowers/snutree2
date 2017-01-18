
class Process:
    '''

    Suppose we wrote this:

        @Process(initializer, start_index)
        def process(result, item):
            accumulate(result, item)
            return

    The returned function is of the form `process(iterable)`: For each
    `item` in `iterable`, it performs `accumulate(result, item)` where `result`
    is initialized to the value returned by `initializer()`. (The parameter
    `start_index` is used for error reporting.)

    '''

    def __init__(self, result_type=list, start_index=1):
        self.result_type = result_type
        self.start_index = start_index

    def __call__(self, accumulate_function):

        def accumulate_function_wrapped(iterable):

            result_container = self.result_type()
            index = self.start_index
            try:
                for item in iterable:
                    accumulate_function(result_container, item)
                    index += 1
            except:
                # TODO use a real error
                raise Exception('Error in row {}'.format(index))

            return result_container

        return accumulate_function_wrapped

def iterate(process_and_store, initializer, start_index=1):

    def iterated(iterable):

        container = initializer()
        index = start_index
        try:
            for item in iterable:
                process_and_store(item, container)
                index += 1
        except:
            # TODO use a real error, replace "row" with something more
            # appropriate
            raise Exception('Error in row {}'.format(index))

        return container

    return iterated

