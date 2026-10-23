import React from 'react';
import {render} from '@testing-library/react-native';
import App from '../App';
test('écran principal',()=>{expect(render(<App/>).getByText('ADF Mobile Reference')).toBeTruthy();});
