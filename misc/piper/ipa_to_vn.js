import { ipaToVie } from '@vuadu/ipa-to-vie';

const ipa = process.argv[2];
function ipa_to_vn(ipa) {
    return ipaToVie(ipa);
}
console.log(ipa_to_vn(ipa));