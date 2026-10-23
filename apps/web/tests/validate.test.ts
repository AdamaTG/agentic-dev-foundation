import {describe,it,expect} from 'vitest';
import {validDescription} from '../lib/validate';
describe('signalement',()=>{it('rejette texte vide',()=>expect(validDescription('  ')).toBe(false));it('accepte une description',()=>expect(validDescription('Déchet')).toBe(true));});
