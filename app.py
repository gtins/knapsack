from flask import Flask, request, render_template, jsonify

# Strategy Pattern Implementation
class KnapsackStrategy:
    def solve(self, items, capacity):
        pass

class RecursiveStrategy(KnapsackStrategy):
    def solve(self, items, capacity):
        # Initialize memoization cache
        self.memo = {}
        result = self._solve_recursive(items, capacity, 0)
        # Return both max value and selected items
        return {
            'max_value': result[0],
            'selected_items': self._get_selected_items(items, capacity, 0)
        }
    
    def _solve_recursive(self, items, capacity, index):
        # Base case: no items left or no capacity
        if index == len(items) or capacity == 0:
            return 0, []
        
        # Check if we've already solved this subproblem
        if (capacity, index) in self.memo:
            return self.memo[(capacity, index)]
        
        # If current item is too heavy, skip it
        if items[index]['weight'] > capacity:
            result = self._solve_recursive(items, capacity, index + 1)
            self.memo[(capacity, index)] = result
            return result
        
        # Two choices: include current item or skip it
        # Choice 1: Skip current item
        skip_value, skip_items = self._solve_recursive(items, capacity, index + 1)
        
        # Choice 2: Include current item
        include_value, include_items = self._solve_recursive(
            items, 
            capacity - items[index]['weight'], 
            index + 1
        )
        include_value += items[index]['value']
        include_items = include_items + [index]
        
        # Take the better choice
        if include_value > skip_value:
            result = (include_value, include_items)
        else:
            result = (skip_value, skip_items)
            
        self.memo[(capacity, index)] = result
        return result
    
    def _get_selected_items(self, items, capacity, index):
        if index == len(items) or capacity == 0:
            return []
            
        if items[index]['weight'] > capacity:
            return self._get_selected_items(items, capacity, index + 1)
        
        # Check if we should include this item
        include_value = 0
        if capacity >= items[index]['weight']:
            next_value, _ = self._solve_recursive(
                items, 
                capacity - items[index]['weight'], 
                index + 1
            )
            include_value = items[index]['value'] + next_value
        
        skip_value, _ = self._solve_recursive(items, capacity, index + 1)
        
        if include_value > skip_value:
            return [index] + self._get_selected_items(
                items, 
                capacity - items[index]['weight'], 
                index + 1
            )
        else:
            return self._get_selected_items(items, capacity, index + 1)

# Factory for creating strategies
class KnapsackStrategyFactory:
    @staticmethod
    def get_strategy(strategy_name):
        if strategy_name == "recursive":
            return RecursiveStrategy()
        # You can add more strategies here in the future
        else:
            raise ValueError(f"Unknown strategy: {strategy_name}")

# Flask application
app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/solve', methods=['POST'])
def solve():
    data = request.get_json()
    items = data.get('items', [])
    capacity = data.get('capacity', 0)
    strategy_name = data.get('strategy', 'recursive')
    
    # Get the appropriate strategy
    strategy = KnapsackStrategyFactory.get_strategy(strategy_name)
    
    # Solve the problem
    result = strategy.solve(items, capacity)
    
    # Format the response
    selected_indices = result['selected_items']
    selected_items = [items[i] for i in selected_indices]
    
    return jsonify({
        'max_value': result['max_value'],
        'selected_items': selected_items,
        'selected_indices': selected_indices
    })

if __name__ == '__main__':
    app.run(debug=True)