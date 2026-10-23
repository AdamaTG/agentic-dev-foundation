// Copy into the Expo project after installing jest-expo and @testing-library/react-native.
import { render, screen } from '@testing-library/react-native';
import HomeScreen from '../../app/index'; // adapt import to your app

test('Home page renders', () => {
  render(<HomeScreen />);
  expect(screen.getByTestId('home-screen')).toBeTruthy();
});
