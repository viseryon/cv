import random

with open('D:\Python_F\projekty\slowa.txt', 'r', encoding='utf-8') as plik:
    slowa = plik.readlines()

print()
print('-----------------------')
print("Witaj w grze 'hangman'!")
print('-----------------------')
print()

while True:

    word = random.choice(slowa)
    word = word.replace('\n', '')
    word = word.upper()

    strzaly = []
    popr_strzaly = []
    hp = 7

    print()
    print('Spróbuj zgadnąć moje słowo!')
    print('- ' * len(word))
    print(f'Słowo ma {len(word)} liter.')
    print()
    # print(word)

    def wszystkie_strzaly():
        tmp = ''
        for a in strzaly:
            tmp += a + ' '
        return tmp

    def czy_legit():

        print('-----------------')
        litera = input('Wybierz literę: ').upper()
        print('-----------------')
        litera = litera.upper()

        if litera not in 'ABCDEFGHJIKLMNOPRSTUVXWYZQĄĘÓŁŚŻŹĆŃ':
            print()
            print('To nie jest litera!')
            print()
            return czy_legit()
        elif litera in strzaly:
            print()
            print('To już było, coś innego!')
            print()
            print('Twoje strzały: ' + wszystkie_strzaly())
            print()
            return czy_legit()
        else:
            return litera

    #  gra tu
    while hp > 0:

        litera = czy_legit()

        strzaly.append(litera)
        if litera in word:
            print()
            print('Trafiony!')
            print()
            popr_strzaly.append(litera)
        else:
            hp -= 1
            print()
            if hp == 0:
                break
            print('Pudło! Tracisz jedno życie!')
            print(f'Pozostało Ci {hp} żyć.')
            print()

        covered = ''
        for letter in word:
            if letter in popr_strzaly:
                covered += letter + ' '
            else:
                covered += '- '

        print(covered)

        if '-' not in covered:
            print()
            print('+++++++++++++++++++++++++++++')
            print('Brawo! Zgadłeś tajemne słowo!')
            print('+++++++++++++++++++++++++++++')
            print()
            break

    if hp == 0:
        print('-' * (len(word) + 20))
        print('Koniec gry!')
        print('Tajne słowo to: ' + word + ' !')
        print('-' * (len(word) + 20))
        print()

    taknie = input('Jeszcze jedna gra? (Y/N): ').upper()
    if taknie == 'N':
        print()
        print('--          --')
        print('Dzięki za grę!')
        print('--          --')
        print()
        break
    elif taknie == 'Y':
        pass
    else:
        break

