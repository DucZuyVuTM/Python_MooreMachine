from collections import defaultdict


class MooreMachine:
    def __init__(self):
        self.transitions = {
            'k0': {
                'swap': [{'cond': None, 'next_state': 'k5'}]
            },
            'k1': {
                'swap': [{'cond': None, 'next_state': 'k4'}]
            },
            'k2': {
                'lower': [{'cond': None, 'next_state': 'k1'}],
                'bend': [{'cond': None, 'next_state': 'k6'}]
            },
            'k3': {
                'bend': [
                    {'cond': {'var': 'd', 'value': 1}, 'next_state': 'k1'},
                    {'cond': {'var': 'd', 'value': 0}, 'next_state': 'k0'},
                ]
            },
            'k4': {
                'tag': [{'cond': None, 'next_state': 'k3'}]
            },
            'k5': {
                'lower': [{'cond': None, 'next_state': 'k0'}],
                'swap': [{'cond': None, 'next_state': 'k4'}],
                'bend': [{'cond': None, 'next_state': 'k2'}]
            },
            'k6': {}
        }
        self.state_outputs = {
            'k0': 'X1', 'k1': 'X0', 'k2': 'X1', 'k3': 'X0',
            'k4': 'X1', 'k5': 'X1', 'k6': 'X0'
        }
        self.current_state = 'k1'
        self.variables = {}
        self.methods_seen = defaultdict(int)
        # Build adjacency list for has_path_to optimization
        self.adjacency_list = defaultdict(set)
        for state, methods in self.transitions.items():
            for method, transitions in methods.items():
                for transition in transitions:
                    next_state = transition['next_state']
                    self.adjacency_list[state].add(next_state)

    def assign_var(self, name, value):
        self.variables[name] = value

    def _get_transition(self, possible_transitions):
        for transition in possible_transitions:
            cond = transition.get('cond')
            if cond is None:
                return transition
            var_name = cond['var']
            required_value = cond['value']
            current_value = self.variables.get(var_name, None)
            if current_value is not None and current_value == required_value:
                return transition
        return None

    def go(self, method):
        all_methods = set()
        for methods in self.transitions.values():
            all_methods.update(methods.keys())
        if method not in all_methods:
            return 'unknown'
        current_transitions = self.transitions.get(self.current_state, {})
        if method not in current_transitions:
            return 'unsupported'
        possible_transitions = current_transitions[method]
        selected = self._get_transition(possible_transitions)
        if selected is None:
            return 'unsupported'
        self.current_state = selected['next_state']
        self.methods_seen[method] += 1
        return None

    def seen_method(self, method):
        return self.methods_seen.get(method, 0)

    def get_output(self):
        return self.state_outputs[self.current_state]

    def has_path_to(self, state):
        visited = set()
        queue = self.initialize_bfs()
        while queue:
            current = queue.pop(0)
            visited.add(current)
            result = self.process_state(current, state, visited, queue)
            if result is True:
                return True
        return False

    def initialize_bfs(self):
        return [self.current_state]

    def process_state(self, current, target_state, visited, queue):
        current_transitions = self.transitions.get(current, {})
        return self.explore_transitions(current_transitions,
                                        target_state, visited, queue)

    def explore_transitions(self, transitions, target_state, visited, queue):
        for method, transition_list in transitions.items():
            for transition in transition_list:
                next_state = transition['next_state']
                if next_state == target_state:
                    return True
                if next_state not in visited:
                    queue.append(next_state)
        return None


def main():
    return MooreMachine()


def test():
    # Follow the example sequence and ensure 100% branch coverage
    obj = main()
    assert obj.assign_var('d', 0) is None
    assert obj.go('leer') == 'unknown'
    assert obj.go('swap') is None  # k1 -> k4 (tests line 61 True)
    assert obj.get_output() == 'X1'  # k4
    assert obj.go('coast') == 'unknown'
    assert obj.go('tag') is None  # k4 -> k3 (tests line 61 True)
    assert obj.get_output() == 'X0'  # k3
    assert obj.go('leer') == 'unknown'
    assert obj.go('bend') is None
    assert obj.get_output() == 'X1'  # k0
    assert obj.go('swap') is None  # k0 -> k5 (tests line 61 True)
    assert obj.seen_method('swap') == 2
    assert obj.get_output() == 'X1'  # k5
    assert obj.go('lower') is None  # k5 -> k0 (tests line 61 True)
    assert obj.get_output() == 'X1'  # k0
    assert obj.go('leer') == 'unknown'
    assert obj.seen_method('tag') == 1
    assert obj.go('swap') is None  # k0 -> k5
    assert obj.get_output() == 'X1'  # k5
    assert obj.go('bend') is None  # k5 -> k2
    assert obj.get_output() == 'X1'  # k2
    assert obj.go('coast') == 'unknown'
    assert obj.go('bend') is None  # k2 -> k6
    assert obj.has_path_to('k4') is False
    assert obj.get_output() == 'X0'  # k6
    assert obj.go('bend') == 'unsupported'

    # Additional tests for 100% branch coverage
    # Test k3 with d=1
    obj = main()
    obj.assign_var('d', 1)
    obj.go('swap')  # k1 -> k4
    obj.go('tag')  # k4 -> k3
    assert obj.go('bend') is None
    assert obj.current_state == 'k1'

    # Test k3 with unsupported condition (d not matching)
    obj = main()
    obj.current_state = 'k3'
    obj.assign_var('d', 2)  # d=2 does not match any condition
    assert obj.go('bend') == 'unsupported'

    # Test k2 with lower
    obj = main()
    obj.current_state = 'k2'
    assert obj.go('lower') is None  # k2 -> k1 (tests line 61 True)
    assert obj.current_state == 'k1'

    # Test k5 with swap
    obj = main()
    obj.current_state = 'k5'
    assert obj.go('swap') is None  # k5 -> k4 (tests line 61 True)
    assert obj.current_state == 'k4'

    # Additional test for line 75 True
    obj = main()
    obj.current_state = 'k3'
    assert obj.go('swap') == 'unsupported'

    # Test has_path_to for reachable and unreachable states
    obj = main()
    assert obj.has_path_to('k1') is True
    assert obj.has_path_to('k0') is True  # k1 -> k4 -> k3 -> k0
    obj.current_state = 'k2'
    assert obj.has_path_to('k6') is True  # k2 -> k6
    assert obj.has_path_to('k5') is True  # k2 -> k1 -> k4 -> k3 -> k0 -> k5
    obj.current_state = 'k6'
    assert obj.has_path_to('k6') is False

# DO NOT ADD THIS TO KISPYTHON.RU !!!!!!!!!
if __name__ == "__main__":
    test()
