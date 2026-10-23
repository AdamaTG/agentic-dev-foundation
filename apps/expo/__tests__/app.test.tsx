import React from 'react';
import {render} from '@testing-library/react-native';
import App from '../App';
test('statut visible',()=>{const view=render(<App/>);expect(view.getByTestId('status').props.children).toBe('Prêt');});
